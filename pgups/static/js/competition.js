(function() {
    'use strict';

    angular
    .module('competitionApp', ['ui.bootstrap'])
    .controller('ModalInstanceController', ModalInstanceController)
    .controller('CompetitionController', CompetitionController)
    .config(altTemplateTags);

    function altTemplateTags($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    }

    function CompetitionController($scope, $uibModal, $log) {

        var vm = this;
        vm.openModal = openModal;
        vm.openModalRelay = openModalRelay;

        function openModal() {
            var modalInstance = $uibModal.open({
              animation: true,
              templateUrl: 'modal.html',
              controller: 'ModalInstanceController',
              controllerAs: '$ctrl',
              size: 'md'
            });
        }

        function openModalRelay() {
            var modalInstance = $uibModal.open({
              animation: true,
              templateUrl: 'modalRelay.html',
              controller: 'ModalInstanceController',
              controllerAs: '$ctrl',
              size: 'md'
            });
        }
    }

    function ModalInstanceController($uibModalInstance) {
        var $ctrl = this;

        $ctrl.cancel = function () {
          $uibModalInstance.dismiss('cancel');
        };
    }
})();
