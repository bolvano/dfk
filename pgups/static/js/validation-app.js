(function() {
    'use strict';

    angular
    .module('validationApp', [])
    .config(altTemplateTags)
    .controller('RegFormController', RegFormController)
    .factory('getData', getData)
    .filter('cap', capitalizeWord);

    altTemplateTags.$inject = ['$interpolateProvider'];
    getData.$inject = ['$q', '$window', '$http', '$log', '$location'];
    RegFormController.$inject = ['$scope', '$http', '$timeout', '$window', '$log', 'getData', 'capFilter'];

    function altTemplateTags($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    }

    function getData($q, $window, $http, $log, $location) {

        var urlArr = $location.absUrl().split('/'),
        userrequest_id = urlArr[urlArr.length - 2];

        var url1 = 'http://' + $window.location.host + '/get_competitions/';
        var url2 = 'http://' + $window.location.host + '/get_teams/';

        if(!isNaN(+userrequest_id)) {
            url1 = url1 + userrequest_id + '/';
        }

        var competitions = $http({method: 'GET', url: url1, cache: 'true'});
        var teams = $http({method: 'GET', url: url2, cache: 'true'});

        return $q.all([competitions, teams])
                 .then(function(data){
                     $log.log('data fetched');
                     return data;
                 });
    }

    function capitalizeWord() {
        return function(word) {
            return word.substring(0,1).toUpperCase() + word.slice(1);
        };
    }

    function RegFormController($scope, $http, $timeout, $window, $log, getData, capFilter) {

        var vm = this;

        // settings
        var maxCompetitorsNum = 2; // max number of competitors per person
        var indRequestOnePerson = false; // forbids adding more than one person if no team selected (true/false)

        var personCounter = 1; // used for assigning ids to persons
        var year = new Date().getFullYear(); // current year

        vm.indRequestOnePerson = indRequestOnePerson;
        vm.persons = [{personId: 'person-0', competitors: [{competitorId: 'competitor-0'}] }];
        vm.form = { persons: vm.persons };

        vm.filterCompetition = filterCompetition;
        vm.filterToursByAge = filterToursByAge;
        vm.tourDisable = tourDisable;
        vm.clearPersons = clearPersons;

        vm.addPerson = addPerson;
        vm.removePerson = removePerson;
        vm.addCompetitor = addCompetitor;
        vm.removeCompetitor = removeCompetitor;

        vm.submitRequest = submitRequest;

        activate();

        function activate() {

            getData.then(function(response) {

                var data = response;
                var sourceData = data[0].data.source_data;

                vm.competitions = data[0].data.competition_list;
                vm.teams = data[1].data;

                if (sourceData.hasOwnProperty('competition_id')) {
                    editUserRequest(sourceData, data);
                }

                return data;
            });
        }

        function editUserRequest(sourceData, data) {
            vm.form = sourceData;

            var competitions = data[0].data.competition_list;
            var competitionId = data[0].data.source_data.competition_id;

            var teams = data[1].data;
            var teamId = data[0].data.source_data.team_id;

            // set competition
            for (var i = 0; i < competitions.length; i++) {
                if (competitions[i].id === competitionId) {
                    vm.form.competition = competitions[i];
                }
            }

            // set team
            for (var j = 0; j < teams.length; j++) {
                if (teams[j].id === teamId) {
                    vm.form.team = teams[j];
                }
            }

            disableElement('#competition-select');
            filterCompetition();

            vm.persons = sourceData.persons;

            // timeout waiting for DOM to load
            $timeout(function() {
                for (var k = 0; k < vm.persons.length; k++) {

                    vm.persons[k].first_name = capFilter(vm.persons[k].first_name);
                    vm.persons[k].last_name = capFilter(vm.persons[k].last_name);

                    tourDisable(k);

                    if (vm.persons[k].competitors.length === maxCompetitorsNum) {
                        angular.element( '#add-competitor-' + vm.persons[k].personId ).addClass('disabled');
                    }
                }
            });
        }

        function disableElement(selector) {
            angular.element(selector).prop('disabled', 'disabled');
        }

        function filterCompetition() {

            var range = calcYears();

            if ( vm.form.competition.type.toLowerCase() === 'детские' ) {
                vm.years = range.slice(-15);
            } else if ( vm.form.competition.type.toLowerCase() === 'взрослые' ) {
                vm.years = range.slice(0, -15);
            } else {
                vm.years = range;
            }

            vm.tours = vm.form.competition.tours;
        }

        function calcYears() {

            var oldest = 1936;
            var youngest = 3;
            var range = [];

            for (var i = oldest; i <= (year - youngest); i++) {
                range.push('' + i);
            }

            return range;
        }

        function filterToursByAge(birth_year) {

            return function(item) {
                var age = year - birth_year;
                return item.max_age >= age && item.min_age <= age;
            };
        }

        function tourDisable(personIdx) {

            // setting everything to enabled
            angular.element('.' + vm.persons[personIdx].personId + '-tour-select option').attr('disabled', false);

            // loop each select and set the selected value to disabled in all other selects
            angular.element('.' + vm.persons[personIdx].personId + '-tour-select').each(function() {

                var $this = angular.element(this);

                angular.element('.' + vm.persons[personIdx].personId + '-tour-select').not($this).find('option').each( function(){

                    if(angular.element(this).attr('value') == $this.val())
                        angular.element(this).attr('disabled', true);

                });
            });
        }

        function basicAnimation(id) {
            angular.element('html, body').animate({
                scrollTop: angular.element(id).offset().top
            });
        }

        // remove all but one persons if team changes to none
        function clearPersons() {
            if ( vm.indRequestOnePerson && vm.form.team === null && vm.persons.length > 1 ) {
                for ( var i = vm.persons.length - 1; i >= 1; i-- ) {
                    vm.persons.splice(i, 1);
                }
            }
        }

        function addPerson() {
            vm.persons.push({ 'personId':'person-' + personCounter,
                              'competitors': [{ competitorId: 'competitor-0'}]
                            });
            personCounter++;

            basicAnimation( '#add-person-button' );
        }

        function removePerson(idx) {
            vm.persons.splice(idx, 1);

            basicAnimation( '#remove-person-' + vm.persons[idx-1].personId );
        }

        function addCompetitor(idx) {
            var newCompetitor = vm.persons[idx].competitors.length;
            vm.persons[idx].competitors.push({ 'competitorId':'competitor-' + newCompetitor });

            // if max number of competitors reached, disable add-competitor button
            if ( vm.persons[idx].competitors.length === maxCompetitorsNum ) {
                angular.element( '#add-competitor-' + vm.persons[idx].personId ).addClass('disabled');
            }

            // delayed call, waiting for DOM to update
            $timeout(function() {
                tourDisable(idx);
            });
        }

        function removeCompetitor(personIdx, idx) {
            vm.persons[personIdx].competitors.splice(idx, 1);

            // enable add-competitor button
            angular.element( '#add-competitor-' + vm.persons[personIdx].personId ).removeClass('disabled');

            // delayed call, waiting for DOM to update
            $timeout(function() {
                tourDisable(personIdx);
            });
        }

        function submitRequest() {

            // disabling button to prevent duplicate requests
            angular.element('#submit-request-button').attr('disabled', true).html('Идет отправка заявки...');

            var req = {
                method: 'POST',
                url: 'http://' + $window.location.host + '/regrequest/',
                headers: {
                    'X-CSRFToken' : $scope.csrf_token,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data: angular.toJson(vm.form)
            };

            $http(req)
                .then(function() {

                    notie.alert(1, 'Заявка отправлена! Вы будете перенаправлены на страницу соревнования.', 2);

                    $timeout(function() {
                        $window.location.href = '/competition/' + vm.form.competition.id;
                    }, 4000);

                }, function() {
                    notie.alert(3, 'Произошла ошибка!', 3);
                    angular.element('#submit-request-button').attr('disabled', false).html('Отправить заявку');
                });
        }
    }
})();
