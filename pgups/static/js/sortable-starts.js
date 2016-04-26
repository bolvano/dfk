(function() {
    'use strict';

    angular
    .module('sortableStartsApp', ['ui.sortable', 'ngAnimate'])
    .config(altTemplateTags)
    .controller('SortController', SortController)
    .filter('ucf', capitalizeWord)
    .factory('getStarts', getStarts)
    .directive('fixOnScroll', fixOnScroll);

    altTemplateTags.$inject = ['$interpolateProvider'];
    SortController.$inject = ['$scope', '$log', '$timeout', 'getStarts'];
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

    function SortController($scope, $log, $timeout, getStarts) {

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
            },
              
            prev: function() {
                this.step--;
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

            // TODO: check if any items left in buffer
            // check every list for max-length (5 or 6?)
            // check for duplicate competitors?
            // call submitRequest if valid,
            // display errors otherwise

        }

        function submitRequest() {

            $log.log('baka!');

        }

    }
})();