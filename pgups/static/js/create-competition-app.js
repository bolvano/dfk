(function() {
'use strict';

angular
.module('createCompetitionApp', ['ngAnimate'])
.config(altTemplateTags)
.controller('CreationFormController', CreationFormController)
.factory('initRequest', initRequest);

altTemplateTags.$inject = ['$interpolateProvider'];
initRequest.$inject = ['$http', '$window', '$log', '$location'];
CreationFormController.$inject = ['$scope', '$http', '$timeout', '$window',
                                  '$log', 'filterFilter', 'initRequest'];

function altTemplateTags($interpolateProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
}

function initRequest($http, $window, $log, $location) {

    var initRequest = {
        async: function() {

            var urlArr = $location.absUrl().split('/'),
            competition_id = urlArr[urlArr.length - 2];

            var url = 'http://' +
                      $window.location.host +
                      '/get_ages_distances_styles/';

            if (!isNaN(competition_id)) {
                url = url + competition_id + '/';
            }

            var promise = $http.get(url)
                .then(function (response) {
                    $log.log('ages/styles/distances fetched');
                    return response.data;
            });

            return promise;
        }
    };

    return initRequest;
}

function CreationFormController($scope, $http, $timeout, $window, $log, filterFilter, initRequest) {

    var vm = this;

    vm.data = {};

    vm.edit = false;
    vm.newTour = {out: false};
    vm.newRelay = {out: false};

    vm.genders = [{ name: 'М' }, { name: 'Ж' }];
    vm.gendersRelay = [{ name: 'М' }, { name: 'Ж' }, { name: 'Смешанные'}];

    vm.addTours = addTours;
    vm.addRelays = addRelays;
    vm.clearSelection = clearSelection;
    vm.removeTour = removeTour;
    vm.disableAge = disableAge;
    vm.getFinalList = getFinalList;

    vm.groupTours = groupTours;
    vm.selected = selected;

    vm.generateTours = generateTours;
    vm.tours = [];
    vm.toursRelay = [];

    vm.selectAll = selectAll;
    vm.checkIfAllSelected = checkIfAllSelected;

    vm.step1BtnClick = step1BtnClick;
    vm.step2BtnClick = step2BtnClick;
    vm.step2BtnDisabled = step2BtnDisabled;
    vm.step3BtnClick = step3BtnClick;
    vm.step3BtnDisabled = step3BtnDisabled;
    vm.step5BtnClick = step5BtnClick;
    vm.step6BtnClick = step6BtnClick;

    vm.submitForm = submitForm;

    vm.stepCounter = {
        step: 1,
        next: function() {
            this.step++;
            $window.scrollTo(0, 0);
        },

        prev: function() {
            this.step--;
            $window.scrollTo(0, 0);
        },
        skipNext: function() {
            this.step += 2;
            $window.scrollTo(0, 0);
        },
        skipPrev: function() {
            this.step -= 2;
            $window.scrollTo(0, 0);
        }
    };

    activate();

    function activate() {
        initRequest.async().then(function(response) {
            var data = response;
            vm.fetchedData = angular.fromJson(response);
            vm.data = vm.fetchedData;

            var date_start = new Date(vm.data.date_start);
            vm.data.date_start = date_start;

            var date_finish = new Date(vm.data.date_finish);
            vm.data.date_finish = date_finish;

            if (vm.data.name) {
                vm.edit = true;
                vm.tours = vm.data.tours;
                $timeout(function() {
                    groupTours(vm.data.ages, 2);
                });
            }

            if (!vm.data.toursRelay) {
                vm.data.toursRelay = [];
            }

            return data;
        });
    }

    function selected(arr) {
        return filterFilter(arr, { selected: true });
    }

    function clearSelection(arr) {
        for (var i = 0; i < arr.length; i++) {
            arr[i].selected = false;
        }
    }

    function addTours() {

        vm.newTours = [];
        vm.existingTours = [];
        var ages = selected(vm.data.ages);
        var genders = selected(vm.genders);

        for (var k = 0; k < genders.length; k++) {
            for (var i = 0; i < ages.length; i++) {
                var tour = {
                    'gender': genders[k].name,
                    'style': vm.newTour.style.id,
                    'distance': vm.newTour.distance.id,
                    'name': vm.newTour.style.name + ' ' +
                            vm.newTour.distance.name + ' ' +
                            ages[i].name + ' ' +
                            genders[k].name,
                    'age': ages[i].id,
                    'min_age': ages[i].min_age,
                    'max_age': ages[i].max_age
                };

                if (vm.newTour.out) {
                    tour.out = true;
                }

                vm.newTours.push(tour);
            }
        }

        outer:
        for (var j = 0; j < vm.newTours.length; j++) {
            for (var l = 0; l < vm.data.tours.length; l++) {

                if (vm.newTours[j].name === vm.data.tours[l].name) {
                    vm.existingTours.push(vm.newTours[j]);
                    continue outer;
                }
            }

            vm.newTours[j].new = true;
            vm.data.tours.push(vm.newTours[j]);
        }

        vm.newTour = {out: false};

        $timeout(function() {
            groupTours(vm.data.ages, '.tour-edit-');
        });
    }


    function addRelays() {

        vm.newRelays = [];
        vm.existingRelays = [];
        var ages = selected(vm.data.agesRelay);
        var genders = selected(vm.gendersRelay);

        for (var k = 0; k < genders.length; k++) {
            for (var i = 0; i < ages.length; i++) {
                var tour = {
                    'gender': genders[k].name,
                    'style': vm.newRelay.style.id,
                    'distance': vm.newRelay.distance.id,
                    'name': vm.newRelay.style.name + ' ' +
                            vm.newRelay.distance.name + ' ' +
                            ages[i].name + ' ' +
                            genders[k].name,
                    'age': ages[i].id,
                    'min_age': ages[i].min_age,
                    'max_age': ages[i].max_age
                };

                if (vm.newRelay.out) {
                    tour.out = true;
                }

                vm.newRelays.push(tour);
            }
        }

        outer:
        for (var j = 0; j < vm.newRelays.length; j++) {
            for (var l = 0; l < vm.data.toursRelay.length; l++) {

                if (vm.newRelays[j].name === vm.data.toursRelay[l].name) {
                    vm.existingRelays.push(vm.newRelays[j]);
                    continue outer;
                }
            }

            vm.newRelays[j].new = true;
            vm.data.toursRelay.push(vm.newRelays[j]);
        }

        vm.newRelay = {out: false};

        $timeout(function() {
            groupTours(vm.data.agesRelay, '.relay-edit-');
        });

        vm.clearSelection(vm.data.agesRelay);
        vm.clearSelection(vm.gendersRelay);
    }

    function disableAge(type) {
        if (vm.newTour.out) {
            return false;
        } else if (vm.data.type === '0' && type === false) {
            return true;
        } else if (vm.data.type === '1' && type === true) {
            return true;
        }
        return false;
    }

    function removeTour(name) {
        if (confirm('Удалить дисциплину ' + '"'+ name +'"?')) {
            for (var i = 0; i < vm.data.tours.length; i++) {
                if (vm.data.tours[i].name === name) {
                    vm.data.tours.splice(i, 1);
                    return;
                }
            }
        }
    }

    function groupTours(arr, className) {
        // removing class from every element in collection
        for ( var i = 0; i < arr.length; i++ ) {
            angular.element(className + arr[i].id).removeClass('mb-20');
        }
        // adding class to last element in collection
        for ( var k = 0; k < arr.length; k++ ) {
            angular.element(className + arr[k].id + ':last').addClass('mb-20');
        }
    }

    // Создает список туров из всех возможных комбинаций возрастов, дистанций и стилей
    // toursArr - массив, в которым добавляем созданные туры
    // className - класс элементов, для отступа между группами
    // agesArr, distancesArr, stylesArr - названия массивов в объекте полученных данных
    function generateTours(toursArr, className, agesArr, distancesArr, stylesArr) {
        // Очищаем массив, чтобы не добавлялись дублирующиеся туры
        toursArr.length = 0;
        var idCount = 0;
        var ages = selected(vm.fetchedData[agesArr]);
        var distances = selected(vm.fetchedData[distancesArr]);
        var styles = selected(vm.fetchedData[stylesArr]);

        for (var i = 0; i < ages.length; i++) {
            for (var j = 0; j < distances.length; j++) {
                for (var k = 0; k < styles.length; k++) {

                    toursArr.push({
                        'id': idCount,
                        'age': ages[i].id,
                        'name': ages[i].name +
                                ' лет, ' + distances[j].name +
                                ', ' + styles[k].name,
                        'distance': distances[j].id,
                        'style': styles[k].id
                    });
                    idCount++;
                }
            }
        }

        // Таймаут, ждем загрузки элементов в DOM
        $timeout(function() {
            groupTours(ages, className);
        });
    }

    function selectAll(tours, type) {
        angular.forEach(tours, function(tour) {
            tour.selected = vm[type];
        });
    }

    function checkIfAllSelected(tours, type) {
        vm[type] = tours.every(function(tour) {
            return tour.selected === true;
        });
    }

    function getFinalList(condition, tours) {
        if (condition) {
            return vm.data[tours];
        }
        return selected(vm[tours]);
    }

    function step1BtnClick() {
        if (vm.edit) {
            vm.stepCounter.skipNext();
            vm.groupTours(vm.data.ages, '.tour-edit-');
        } else {
            vm.stepCounter.next();
        }
    }


    function step2BtnClick() {
        vm.stepCounter.next();
        vm.generateTours(vm.tours, '.tour-choices-', 'ages', 'distances', 'styles');
        vm.checkIfAllSelected(vm.tours, 'allToursSelected');
    }

    function step2BtnDisabled() {

        if (!vm.fetchedData) return true;

        return vm.selected(vm.fetchedData.ages).length < 1 ||
               vm.selected(vm.fetchedData.styles).length < 1 ||
               vm.selected(vm.fetchedData.distances).length < 1;
    }

    function step3BtnClick() {
        vm.stepCounter.next();
        vm.groupTours(vm.data.ages, '.tour-final-1-');
    }

    function step3BtnDisabled() {
        return vm.edit ? false : (vm.selected(vm.tours).length === 0);
    }

    function step5BtnClick() {
        vm.stepCounter.next();
        vm.generateTours(vm.toursRelay, '.relay-', 'agesRelay', 'distancesRelay', 'stylesRelay');
        vm.checkIfAllSelected(vm.toursRelay, 'allRelayToursSelected');
    }

    function step6BtnClick() {
        vm.stepCounter.next();
        vm.groupTours(vm.data.ages, '.tour-final-2-');
        vm.groupTours(vm.data.agesRelay, '.relay-final-');
    }

    function submitForm() {

        if (!vm.edit) {
            vm.data.tours = selected(vm.tours);
        }

        // disable button to prevent multiple requests
        angular.element('#create-competition-button').attr('disabled', true).html('Идет сохранение...');

        var req = {
            method: 'POST',
            url: 'http://' + $window.location.host + '/competition_create/',
            headers: {
                'X-CSRFToken' : $scope.csrf_token,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data: angular.toJson(vm.data)
        };

        $http(req)
            .then(function() {

                notie.alert(1, 'Изменения сохраняются... Вы будете перенаправлены на главную страницу.');

                $timeout(function() {
                    $window.location.href = '/';
                }, 4000);

            }, function() {
                notie.alert(3, 'Произошла ошибка!', 3);
                angular.element('#create-competition-button').attr('disabled', false).html('Создать соревнования');
            });
    }

}
})();
