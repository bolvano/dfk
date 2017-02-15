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

            var promise = $http.get('http://' +
                                    $window.location.host +
                                    '/get_relay_starts/' +
                                    competition_id)
                                .then(function (response) {
                                    return response.data;
                                });

            return promise;
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
        getRelays.async().then(function(response) {
            vm.data = response;
            return response;
        });
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
