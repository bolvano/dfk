var validationApp = angular.module('validationApp', []);


// custom config handling conflicting django/angular template tags
validationApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});


// form controller
validationApp.controller('formCtrl', ['$scope',

    function($scope, $http) {

        $scope.persons = [{ id: 'person-0'}, { id: 'person-1'}];

        $scope.form = {persons: $scope.persons};

        // counter resets on document load
        var personCounter = 2;

        $scope.addPerson = function() {
            $scope.persons.push({ 'id':'person-' + personCounter });
            personCounter++;
        };

        $scope.removePerson = function(idx) {
            $scope.persons.splice(idx, 1);
        };

    }
]);
