'use strict';

var validationApp = angular.module('validationApp', []);


// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
validationApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});


// form controller
validationApp.controller('formCtrl', ['$scope',

    function($scope, $http) {

        // adding initial element on load (at least one person per request required)
        $scope.persons = [ { personId: 'person-0',
                             gender: 'М',
                             birth_year: 1998,
                             competitors: [{ competitorId: 'competitor-0'}]
                           }
                         ];

        // adding persons list to form object
        $scope.form = {persons: $scope.persons};

        // calculating year of birth options
        var year = new Date().getFullYear();
        var range = [];
        for ( var i = 1929; i <= ( year - 18 ); i++) {
          range.push(i);
        }

        $scope.years = range;

        // jQuery animation function
        function basicAnimation(id) {

            $('html, body').animate({
                scrollTop: $(id).offset().top
            });
        };

        // person counter resets on document load, setting initial value = 1
        var personCounter = 1;

        // max number of competitors per person
        var maxCompetitorsNum = 2;

        // if no team selected, forbids adding more than one person (true/false)
        $scope.indRequestOnePerson = false;


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
                                  'gender': 'М',
                                  'birth_year': 1998,
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

        };


        // remove competitor
        $scope.removeCompetitor = function(personIdx, idx) {

            $scope.persons[personIdx].competitors.splice(idx, 1);

            // enable add-competitor button
            $( '#add-competitor-' + $scope.persons[personIdx].personId ).removeClass('disabled');

            basicAnimation( '#add-competitor-' + $scope.persons[personIdx].personId );

        };

    }
]);
