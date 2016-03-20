'use strict';

var createCompetitionApp = angular.module('createCompetitionApp', ['ngCookies']);


// handling conflicting django/angular template tags
// (setting {$ $} tags for angular stuff)
createCompetitionApp.config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
});

// form controller
createCompetitionApp.controller( 'creationFormCtrl', function( $scope, $http, $timeout, $cookies ) {

    $scope.data = {};

});
