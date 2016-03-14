var validationApp = angular.module('validationApp', []);


// custom config handling conflicting django/angular template tags
validationApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});

// form controller
validationApp.controller('formCtrl', ['$scope', function($scope, $http) {

    $scope.form = {};

    $scope.persons = [{ id: 'person-0'}, { id: 'person-1'}];

    $scope.addPerson = function() {
        var newPersonNum = $scope.persons.length;
        $scope.persons.push({'id':'person-'+newPersonNum});
    };

    $scope.removePerson = function(idx) {
        $scope.persons.splice(idx, 1);
    };

}]);