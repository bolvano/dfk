$(document).ready(function() {

    "use strict";

    $("#id_competitorMap").attr('value', '{}');

    var filterTours = function(select_id){

        var competition_selector = '#id_competition';
        var competition_id = $(competition_selector).val();
        var person_id = $(select_id).parents(':eq(6)').attr('id').replace(/\D/g,''); // person div
        var pby_selector = '#id_person_set-' + person_id + '-birth_year' + ' option:selected';
        var year = $(pby_selector).val();
        var gender_selector = '#id_person_set-' + person_id + '-gender' + ' option:selected';
        var gender = $(gender_selector).val();
        var request_url = '/get_tours/' + year + '/' + gender + '/' + competition_id + '/';

        $.ajax({
            url: request_url,
            success: function(data){

                $(select_id).empty();

                $.each(data, function(key, value){
                    $(select_id).append('<option value="' + key + '">' + value +'</option>');
                });
            }
        });
    };


    var addCompetitor = function(person) {
        var competitorMap = JSON.parse($("#id_competitorMap").val());
        var count = $('.competitor_div').length;
        var tmplMarkup = $('#competitor-template').html();
        var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
        var newCompetitor = $(compiledTmpl).appendTo(person.find("#competitor-col"));

        competitorMap[newCompetitor.attr('id').replace(/\D/g,'')] = person.attr('id').replace(/\D/g,'');

        $("#id_competitorMap").attr('value', JSON.stringify(competitorMap));
        $('#id_competitor_set-TOTAL_FORMS').attr('value', count + 1);

        var new_tour_id = '#id_competitor_set-' + count.toString() + '-tour';

        filterTours(new_tour_id);
    };

    var addPerson = function() {
        //ev.preventDefault();
        var count = $('#persons-form-container').children().length;
        var tmplMarkup = $('#person-template').html();
        var compiledTmpl = tmplMarkup.replace(/__prefix__/g, count);
        var newPerson = $(compiledTmpl).appendTo("div#persons-form-container");
        $('#id_person_set-TOTAL_FORMS').attr('value', count+1);
        addCompetitor(newPerson);

        // some animate to scroll to view our new form
        $('html, body').animate({
                scrollTop: $("#add-person-button").position().top-200
            }, 800);

    };

    //addPerson();


// Adding

    $("#right").on('click', '.add-person', function(){
        addPerson();
    });

    $("#right").on("click", ".add-competitor", function(ev){
        ev.preventDefault();

        var parent = $(this).parent().parent();
        addCompetitor(parent); //person div
    });


// Removing

    // person div
    $("#right").on("click", ".remove_person", function(e){ //user click on remove text
        e.preventDefault();

        $(this).parent('div').parent('div').hide();

        $(this).parent().parent().find('input[id*="DELETE"]').prop('checked', true);

        var parent_id = $(this).parent().parent().attr('id').replace(/\D/g,'');

        var competitorMap = JSON.parse($("#id_competitorMap").val());

        for(var f in competitorMap) {
            if(competitorMap[f] == parent_id) {
                delete competitorMap[f];
            }
        }

        $("#id_competitorMap").attr('value', JSON.stringify(competitorMap));
    });

    // competitor div
    $("#right").on("click", ".remove-competitor", function(e){ //user click on remove text
        e.preventDefault();

        $(this).parents(':eq(2)').hide();

        $(this).parents(':eq(2)').find('input[id*="DELETE"]').prop('checked', true);

        var competitor_id = $(this).parents(':eq(2)').attr('id').replace(/\D/g,'');

        var competitorMap = JSON.parse($("#id_competitorMap").val());

        delete competitorMap[competitor_id];

        $("#id_competitorMap").attr('value', JSON.stringify(competitorMap));
    });


// Filtering

    $("#right").on("change", 'select[id*="birth_year"]', function(){

        var person = $(this).parent().parent().parent().parent().attr('id');

        var person_competitors = '#' + person + ' .competitor_div';

        $(person_competitors).each(
            function(index) {
                var tour_id = $(this).find('select').attr('id');
                tour_id = '#' + tour_id;
                filterTours(tour_id);
            });
    });

    $("#right").on("change", 'select[id*="gender"]', function(){

        var person = $(this).parent().parent().parent().parent().attr('id');

        var person_competitors = '#' + person + ' .competitor_div';

        $(person_competitors).each(
            function(index) {
                var tour_id = $(this).find('select').attr('id');
                tour_id = '#' + tour_id;
                filterTours(tour_id);
            });
    });

});
