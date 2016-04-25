(function() {
    'use strict';

    angular
    .module('sortableStartsApp', ['ui.sortable'])
    .config(altTemplateTags)
    .controller('SortController', SortController)
    .filter('ucf', capitalizeWord)
    .factory('getStarts', getStarts)
    .directive('fixOnScroll', fixOnScroll);

    altTemplateTags.$inject = ['$interpolateProvider'];
    SortController.$inject = ['$scope', 'getStarts'];
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

                var urlArr = $location.absUrl().split('/');
                var competition_id = urlArr[urlArr.length - 2];

                var promise = $http.get('http://' +
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

                var topClass = attrs.fixOnScroll, // get CSS class from directive's attribute value
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

    function SortController($scope, getStarts) {

        var vm = this;

        activate();

        vm.sortableStartOptions = {
            placeholder: 'single-competitor-sort-highlight',
            connectWith: '.competitor-list-sort',
            opacity: 0.75
        };

        vm.sortableStartsListOptions = {
            placeholder: 'single-start-sort-highlight',
            items: 'div.sortable-start-list',
            opacity: 0.75
        };

        vm.addStart = addStart;
        vm.removeStart = removeStart;

        function activate() {
            getStarts.async().then(function(response) {
                var data = response;
                vm.data = response;
                //adding empty element as a buffer
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
        }

        function removeStart() {}

    }
})();