(function() {
    'use strict';

    angular
    .module('sortableStartsApp', ['ui.sortable'])
    .config(altTemplateTags)
    .controller('SortController', SortController)
    .filter('ucf', capitalize)
    .factory('getStarts', getStarts);

    altTemplateTags.$inject = ['$interpolateProvider'];
    SortController.$inject = ['$scope', '$http', '$window', '$log', 'getStarts'];
    getStarts.$inject = ['$http', '$window', '$log', '$location'];

    function capitalize() {
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

    function SortController($scope, $http, $window, $log, getStarts) {

        var vm = this;

        activate();

        function activate() {
            getStarts.async().then(function(response) {
                var data = response;
                vm.data = response;
                return data;
            });
        }

    function createOptions () {
        var options = {
            placeholder: "app",
            connectWith: ".sortable-start",
        };
        return options;
    }

    $scope.sortableOptions = createOptions();

    }
})();