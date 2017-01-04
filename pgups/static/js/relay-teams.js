(function() {
    'use strict';

    angular
    .module('relayApp', [])
    .config(altTemplateTags)
    .controller('RelayController', RelayController)
    .factory('teamService', teamService);

    altTemplateTags.$inject = ['$interpolateProvider'];
    teamService.$inject = ['$window', '$http', '$location', '$log'];
    RelayController.$inject = ['$scope', '$http', '$timeout', '$window', '$log', 'teamService'];

    function altTemplateTags($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    }

    function teamService($window, $http, $location, $log) {
        var urlArr = $location.absUrl().split('/');
        var relay_id = urlArr[urlArr.length - 2];

        var teamService = {

            getRelayTeams: function() {
                var url = 'http://' + $window.location.host + '/get_relay_teams/' + relay_id + '/';
                var promise = $http.get(url)
                                .then(function(response) {
                                    return response.data;
                                })
                                .catch(function(error) {
                                    $log.error(error);
                                });
                return promise;
            },

            saveRelayTeams: function(teams, csrf_token) {
                var req = {
                    method: 'POST',
                    url: 'http://' + $window.location.host + '/relay_teams/' + relay_id + '/',
                    headers: {
                        'X-CSRFToken' : csrf_token,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    data: angular.toJson(teams)
                };

                return $http(req)
                            .then(function(response) {
                                return response;
                            })
                            .catch(function(error) {
                                $log.error(error);
                            });
            }
        }
        return teamService;
    }

    function RelayController($scope, $http, $timeout, $window, $log, teamService) {
        var vm = this;
        vm.teams = [];
        vm.relayTeams = [];
        vm.addTeam = addTeam;
        vm.removeTeam = removeTeam;
        vm.saveTeams = saveTeams;
        vm.csrf_token = "";

        activate();

        function activate() {
            teamService.getRelayTeams()
                .then(function(response) {
                    vm.relayTeams = response.relayTeams;
                    vm.teams = response.teams;
                });
        }

        function addTeam(form) {
            vm.relayTeams.push(vm.selectedTeam);
            vm.teams.splice(vm.teams.indexOf(vm.selectedTeam), 1);
            vm.selectedTeam = null;

            // Ресет формы
            form.$setPristine();
            form.$setUntouched();
        }

        function removeTeam(idx) {
            vm.teams.push(vm.relayTeams[idx]);
            vm.relayTeams.splice(idx, 1);
        }

        function saveTeams() {
            teamService.saveRelayTeams(vm.relayTeams, vm.csrf_token)
                          .then(function(response) {
                                notie.alert(1, 'Изменения сохранены', 2);
                                activate();
                          })
                          .catch(function() {
                                notie.alert(3, 'Произошла ошибка!', 5);
                          });
        }

    }
})();
