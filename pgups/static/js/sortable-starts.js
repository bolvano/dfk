(function() {
    'use strict';

    angular
    .module('sortableStartsApp', ['ui.sortable', 'ngAnimate'])
    .config(altTemplateTags)
    .controller('SortController', SortController)
    .filter('cap', capitalizeWord)
    .factory('getStarts', getStarts)
    .directive('fixOnScroll', fixOnScroll);

    altTemplateTags.$inject = ['$interpolateProvider'];
    SortController.$inject = ['$scope', '$log', '$timeout', '$window', '$http', 'getStarts'];
    getStarts.$inject = ['$http', '$window', '$log', '$location'];
    fixOnScroll.$inject = ['$window'];

    function capitalizeWord() {
        return function(word) {
            return word.substring(0,1).toUpperCase() + word.slice(1);
        };
    }

    function altTemplateTags($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    }

    function getStarts($http, $window, $log, $location) {
        var starts = {
            async: function() {

                var urlArr = $location.absUrl().split('/'),
                    competition_id = urlArr[urlArr.length - 2],

                    promise = $http.get('http://' +
                                        $window.location.host +
                                        '/get_competition_starts/' +
                                        competition_id)

                .then(function (response) {
                    $log.log('starts fetched');
                    return response.data;
                });

                return promise;
            }
        };
        return starts;
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

    function SortController($scope, $log, $timeout, $window, $http, getStarts) {

        var vm = this;

        activate();

        vm.sortableStartOptions = {
            placeholder: 'single-competitor-sort-highlight',
            connectWith: '.connected-competitors',
            opacity: 0.75
        };

        vm.sortableStartsListOptions = {
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

        vm.addStart = addStart;
        vm.removeStart = removeStart;
        vm.validateStarts = validateStarts;
        vm.submitRequest = submitRequest;

        function activate() {
            getStarts.async().then(function(response) {
                var data = response;

                vm.data = response;

                //adding an empty list to act as a buffer
                vm.data.starts_list.unshift({ role: 'buffer', competitors: []});

                return data;
            });
        }

        function basicAnimation(id) {
            angular.element('html, body').animate({
                scrollTop: angular.element(id).offset().top
            });
        }

        function addStart() {
            vm.data.starts_list.push({
                'competitors': []
            });

            basicAnimation('#add-start-button');
        }

        function removeStart(idx) {

            var removedCompetitors = vm.data.starts_list[idx].competitors,
                buffer = vm.data.starts_list[0].competitors;

            // move competitors to buffer
            removedCompetitors.forEach(function(item){
                buffer.push(item);
            });

            vm.data.starts_list.splice(idx, 1);

        }

        function validateStarts() {

            var startList = vm.data.starts_list,
                tooLongLists = [];
                //maxLength = 6; // value would be retrieved from vm.data

            if (!vm.maxLength) {

                notie.alert(3, 'Укажите количество дорожек!', 5);

            } else {

                for (var i = 1; i < startList.length; i++) {
                    if (startList[i].competitors.length > vm.maxLength) {
                        tooLongLists.push(i);
                    }
                }

                if (startList[0].competitors.length > 0) {
                    notie.alert(3, 'В буфере остались нераспределённые участники!', 5);
                } else if (tooLongLists.length > 0) {
                    var startsPlural = tooLongLists.length === 1 ? 'заплыве' : 'заплывах';
                    notie.alert(3, 'В '+ startsPlural + ' № ' + tooLongLists.join(', ') + ' более ' + vm.maxLength + ' участников!', 5);
                } else {
                    notie.alert(1, 'Бублик!', 3);
                    submitRequest();
                }
            }
        }

        function submitRequest() {

            $log.log('baka!');

            vm.data.max_length = vm.maxLength;

            /*
            // disabling button to prevent duplicate requests
            angular.element('#submit-request-button').attr('disabled', true).html('Идет сохранение заплывов...');

            var req = {
                method: 'POST',
                url: 'http://' + $window.location.host + '...', // insert url here
                headers: {
                    'X-CSRFToken' : $scope.csrf_token,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data: angular.toJson(vm.data)
            };

            $http(req)
                .then(function() {

                    notie.alert(1, 'Заплывы сохранены! Вы будете перенаправлены на текущую сетку стартов.', 2);

                    $timeout(function() {
                        $window.location.href = '/someURL/'; // insert url here
                    }, 4000);

                }, function() {
                    notie.alert(3, 'Произошла ошибка!', 3); // custom error text if duplicates or other errors
                    angular.element('#submit-request-button').attr('disabled', false).html('Сохранить заплывы');
                });
            */

        }

    }
})();