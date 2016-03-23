'use strict';

var validationApp = angular.module('validationApp', []);


// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
validationApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});


// form controller
validationApp.controller( 'formCtrl', function( $scope, $http, $timeout ) {


        // initial data request
        var initRequest = $http.get( 'http://' + window.location.host + '/get_competitions/' )
            .then(function(response) {

                console.log($scope.csrf_token);

                console.log('data fetched');
                $scope.fetchedData = angular.fromJson(response);
                return response;

            });

        var teamRequest = $http.get( 'http://' + window.location.host + '/get_teams/' )
            .then(function(response) {

                console.log('teams fetched');
                $scope.teamsData = angular.fromJson(response);
                return response;

            });

        // person counter resets on document load, setting initial value = 1
        var personCounter = 1;

        // max number of competitors per person
        var maxCompetitorsNum = 2;

        // saving year of birth options
        var year = new Date().getFullYear();
        var range = [];
        for ( var i = 1936; i <= ( year - 3 ); i++) {
          range.push(i);
        };

        // if no team selected, forbids adding more than one person (true/false)
        $scope.indRequestOnePerson = false;

        // adding initial element on load (at least one person per request required)
        $scope.persons = [ { personId: 'person-0',
                             competitors: [{ competitorId: 'competitor-0'}]
                           }
                         ];

        // adding persons list to form object
        $scope.form = { persons: $scope.persons };

        // birth year options
        $scope.years = range;


        // filtering data in personsForm based on selected competition
        $scope.filterCompetition = function() {

            // filtering birth year options by competition type
            if ( $scope.form.competition.type.toLowerCase() === 'детские' ) {

                $scope.years = range.slice(-15);

            } else {

                $scope.years = range.slice(0, -15);

            };

            // adding tour options to competitorForm
            $scope.tours = $scope.form.competition.tours;

        };


        // filtering tours by age
        $scope.filterToursByAge = function(birth_year) {

            return function(item) {

                // calculating persons age
                var age = year - birth_year;

                return item['max_age'] >= age && item['min_age'] <= age;

            }
        };


        // disabling tour option if already selected elsewhere
        var tourDisable = function(personIdx) {

            // setting everything to enabled
            $('.' + $scope.persons[personIdx].personId + '-tour-select option').attr('disabled', false);

            // loop each select and set the selected value to disabled in all other selects
            $('.' + $scope.persons[personIdx].personId + '-tour-select').each(function() {

                var $this = $(this);

                $('.' + $scope.persons[personIdx].personId + '-tour-select').not($this).find('option').each( function(){

                    if($(this).attr('value') == $this.val())
                        $(this).attr('disabled', true);

                });

            }); 

        };


        $scope.tourDisable = tourDisable;


        // jQuery animation
        function basicAnimation(id) {

            $('html, body').animate({
                scrollTop: $(id).offset().top
            });
        };


        // remove all but one persons if team changes to none
        $scope.clearPersons = function() {

            if ( $scope.indRequestOnePerson && $scope.form.team === '' && $scope.persons.length > 1 ) {
                for ( var i = $scope.persons.length - 1; i >= 1; i-- ) {
                    $scope.persons.splice(i, 1);
                }
            }

        };


        // add person
        $scope.addPerson = function() {

            $scope.persons.push({ 'personId':'person-' + personCounter,
                                  'competitors': [{ competitorId: 'competitor-0'}]
                                });
            personCounter++;

            basicAnimation( '#add-person-button' );

        };


        // remove person
        $scope.removePerson = function(idx) {

            $scope.persons.splice(idx, 1);

            basicAnimation( '#remove-person-' + $scope.persons[idx-1].personId );

        };


        // add competitor
        $scope.addCompetitor = function(idx) {

            var newCompetitor = $scope.persons[idx].competitors.length;
            $scope.persons[idx].competitors.push({ 'competitorId':'competitor-' + newCompetitor });

            // if max number of competitors reached, disable add-competitor button
            if ( $scope.persons[idx].competitors.length === maxCompetitorsNum ) {
                $( '#add-competitor-' + $scope.persons[idx].personId ).addClass('disabled');
            };

            basicAnimation( '#add-competitor-' + $scope.persons[idx].personId );

            // delayed call, waiting for DOM to update
            $timeout(function() {
                tourDisable(idx);
            }, 500);

        };


        // remove competitor
        $scope.removeCompetitor = function(personIdx, idx) {

            $scope.persons[personIdx].competitors.splice(idx, 1);

            // enable add-competitor button
            $( '#add-competitor-' + $scope.persons[personIdx].personId ).removeClass('disabled');

            basicAnimation( '#add-competitor-' + $scope.persons[personIdx].personId );

            // delayed call, waiting for DOM to update
            $timeout(function() {
                tourDisable(personIdx);
            }, 500);

        };


        // submit form data
        $scope.submitRequest = function() {

            // disabling submit button to prevent duplicate requests
            $('#submit-request-button').attr('disabled', true).html('Идет отправка заявки...');

            var req = {
             method: 'POST',
             url: 'http://' + window.location.host + '/regrequest/',
             headers: {
                'X-CSRFToken' : $scope.csrf_token,
                'Content-Type': 'application/x-www-form-urlencoded'
             },
             data: angular.toJson($scope.form)
            };

            var postRequest = $http(req)
                .then(function(response) {

                    // displaying success message
                    notie.alert(1, 'Заявка отправлена! Страница сейчас обновится', 5);

                    // delayed page refreshing
                    $timeout(function() {
                        location.reload();
                    }, 2000);

                }, function(response) {
                    notie.alert(3, 'Произошла ошибка!', 3);
                    $('#submit-request-button').attr('disabled', false).html('Отправить заявку');
                });

        };

    }
);
