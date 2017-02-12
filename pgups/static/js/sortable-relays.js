(function() {
'use strict';

angular
.module('sortableRelaysApp', ['ui.sortable', 'ngAnimate'])
.config(altTemplateTags)
.controller('SortController', SortController)
.factory('getRelays', getRelays)
.directive('fixOnScroll', fixOnScroll);

altTemplateTags.$inject = ['$interpolateProvider'];
SortController.$inject = ['$scope', '$timeout', '$window', '$http', 'getRelays'];
getRelays.$inject = ['$http', '$window', '$location'];
fixOnScroll.$inject = ['$window'];

function altTemplateTags($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
}

function getRelays($http, $window, $location) {
    var relayService = {
        async: function() {
            var urlArr = $location.absUrl().split('/');
            var competition_id = urlArr[urlArr.length - 2];

            var TEST_DATA = {
                              "competition_id": 8,
                              "relays": [

                                    { role: 'buffer', teams: [
                                        {
                                          "tour_name": "\u043d\u0430 \u0441\u043f\u0438\u043d\u0435 4 x 50 \u043c. 18-29 \u0421",
                                          "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-I",
                                          "id": 65,
                                          "lane": 2
                                        },
                                        {
                                          "tour_name": "\u043d\u0430 \u0441\u043f\u0438\u043d\u0435 4 x 50 \u043c. 18-29 \u0421",
                                          "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-II",
                                          "id": 66,
                                          "lane": 3
                                        },
                                        {
                                          "tour_name": "\u043d\u0430 \u0441\u043f\u0438\u043d\u0435 4 x 50 \u043c. 18-29 \u0421",
                                          "name": "Мжвяки-II",
                                          "id": 66,
                                          "lane": 3
                                        }
                                    ]},

                                    {
                                      "name": "\u042d\u0441\u0442\u0430\u0444\u0435\u0442\u0430 4 x 50 \u043c. \u043d\u0430 \u0441\u043f\u0438\u043d\u0435 18-29 \u0421",
                                      "id": 18,
                                      "num": 1,
                                      "teams": [
                                        {
                                          "tour_name": "\u043d\u0430 \u0441\u043f\u0438\u043d\u0435 4 x 50 \u043c. 18-29 \u0421",
                                          "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-I",
                                          "id": 65,
                                          "lane": 2
                                        },
                                        {
                                          "tour_name": "\u043d\u0430 \u0441\u043f\u0438\u043d\u0435 4 x 50 \u043c. 18-29 \u0421",
                                          "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-II",
                                          "id": 66,
                                          "lane": 3
                                        }
                                      ]
                                    },
                                    {
                                      "name": "\u042d\u0441\u0442\u0430\u0444\u0435\u0442\u0430 4 x 50 \u043c. \u043d\u0430 \u0441\u043f\u0438\u043d\u0435 30-39 \u0421",
                                      "id": 19,
                                      "num": 2,
                                      "teams": [
                                        {
                                          "tour_name": "\u043d\u0430 \u0441\u043f\u0438\u043d\u0435 4 x 50 \u043c. 30-39 \u0421",
                                          "name": "\u0414\u0424\u041a \u041f\u0413\u0423\u041f\u0421-I",
                                          "id": 64,
                                          "lane": 3
                                        }
                                      ]
                                    }
                              ],
                              "competition_name": "test"
                            }

            /*
            var promise = $http.get('http://' +
                                    $window.location.host +
                                    '/get_relay_starts/' +
                                    competition_id)
                                .then(function (response) {
                                    return response.data;
                                });
            */

            return TEST_DATA;

            // return promise;
        }
    };
    return relayService;
}

function fixOnScroll($window) {
    var win = angular.element($window);

    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            // get CSS class from directive's attribute value
            var topClass = attrs.fixOnScroll,
                offsetTop = element.offset().top,
                width = element.width();

            win.on('scroll', function () {
                if (win.scrollTop() >= offsetTop) {
                    element.addClass(topClass);
                    element.width(width);
                } else {
                    element.removeClass(topClass);
                }
            });
        }
    };
}

function SortController($scope, $timeout, $window, $http, getRelays) {
    var vm = this;

    activate();

    vm.sortableRelayOptions = {
        placeholder: 'single-competitor-sort-highlight',
        connectWith: '.connected-competitors',
        opacity: 0.75
    };

    vm.sortableRelaysListOptions = {
        placeholder: 'single-start-sort-highlight',
        opacity: 0.75
    };

    vm.stepCounter = {
        step: 1,
        next: function() {
            this.step++;
            $window.scrollTo(0, 0);
        },
        prev: function() {
            this.step--;
            $window.scrollTo(0, 0);
        }
    };

    vm.addRelay = addRelay;
    vm.removeRelay = removeRelay;
    vm.validateRelays = validateRelays;
    vm.confirmOnEnter = confirmOnEnter;
    vm.submitRequest = submitRequest;

    function activate() {
        vm.data = getRelays.async();

        console.log(vm.data);

        /*
        getRelays.async().then(function(response) {
            vm.data = response;

            //adding an empty list to act as a buffer
            vm.data.relayCDSGs.unshift({ role: 'buffer', competitors: []});

            console.log(vm.data);

            return response;
        });
        */
    }

    function basicAnimation(id) {
        angular.element('html, body').animate({
            scrollTop: angular.element(id).offset().top
        });
    }

    function addRelay() {
        vm.data.relays.push({
            'teams': [],
            'editable': true
        });

        basicAnimation('#add-start-button');
    }

    function removeRelay(idx) {
        var removedTeams = vm.data.relays[idx].teams,
            buffer = vm.data.relays[0].teams;

        angular.forEach(removedTeams, function(team, i){
            buffer.push(team);
        });

        vm.data.relays.splice(idx, 1);
    }

    function validateRelays() {
        var relayList = vm.data.relays,
            tooLongLists = [];

        if (!vm.maxLength) {
            notie.alert(3, 'Укажите количество дорожек!', 5);
        } else {
            angular.forEach(relayList, function(relay, i) {
                if (relay.teams.length > vm.maxLength) {
                    tooLongLists.push(i);
                }
            });

            if (relayList[0].teams.length > 0) {
                notie.alert(3, 'В буфере остались нераспределённые команды!', 5);
            } else if (tooLongLists.length > 0) {
                var relaysPlural = tooLongLists.length === 1 ? 'заплыве' : 'заплывах';
                notie.alert(3, 'В '+ relaysPlural + ' № ' + tooLongLists.join(', ') + ' более ' + vm.maxLength + ' участников!', 5);
            } else {
                submitRequest();
            }
        }
    }

    function confirmOnEnter(event, relay) {
        if (event.keyCode === 13) {
            relay.editable = false;
        }
    }

    function submitRequest() {
        vm.data.max_length = vm.maxLength;

        // disabling button to prevent duplicate requests
        angular.element('#submit-request-button').attr('disabled', true).html('Идет сохранение заплывов...');

        var req = {
            method: 'POST',
            url: 'http://' + $window.location.host + '/competition_relays_sort/' + vm.data.competition_id + '/',
            headers: {
                'X-CSRFToken' : $scope.csrf_token,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: angular.toJson(vm.data)
        };

        $http(req)
            .then(function() {
                notie.alert(1, 'Данные сохранены! Вы будете перенаправлены на текущую сетку эстафетных заплывов.', 2);

                $timeout(function() {
                    $window.location.href = '/competition/relay_starts/' + vm.data.competition_id + '/';
                }, 4000);

            }, function(response) {
                notie.alert(3, 'Произошла ошибка: ' + response.status + ' ' + response.statusText, 3);
                angular.element('#submit-request-button').attr('disabled', false).html('Сохранить заплывы');
            });
    }
}
})();
