(function() {
    'use strict';

    angular
    .module('sortableStartsApp', ['ui.sortable'])
    .config(altTemplateTags)
    .controller('SortController', SortController)
    .filter('ucf', capitalizeWord)
    .factory('getStarts', getStarts);

    altTemplateTags.$inject = ['$interpolateProvider'];
    SortController.$inject = ['$scope', 'getStarts'];
    getStarts.$inject = ['$http', '$window', '$log', '$location'];

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

                var url = $location.absUrl();
                var urlArr = url.split('/');
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

    function SortController($scope, getStarts) {

        var vm = this;

        activate();

        vm.sortableOptions = {
            placeholder: 'single-competitor-sort-highlight',
            connectWith: '.sortable-start',
            opacity: 0.75
        };

        vm.sortableStartList = {
            placeholder: 'single-start-sort-highlight',
            items: 'div.sortable-start-list',
            opacity: 0.75
        };

        function activate() {
            getStarts.async().then(function(response) {
                var data = response;
                vm.data = response;
                //adding empty element as a buffer
                vm.data.starts_list.unshift({ role: 'buffer', competitors: []});
                return data;
            });
        }

    }
})();