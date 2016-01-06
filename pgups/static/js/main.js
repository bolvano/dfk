$(document).ready(function() {

	$("#id_competitorMap").attr('value', '{}');


    var filterTours = function(select_id){

    	person_id = $(select_id).parent().parent().attr('id').replace(/\D/g,''); // person div

    	pby_selector = '#id_person_set-' + person_id + '-birth_year' + ' option:selected';
        year = $(pby_selector).val();

        gender_selector = '#id_person_set-' + person_id + '-gender' + ' option:selected';
        gender = $(gender_selector).val();
        request_url = '/get_tours/' + year + '/' + gender + '/';

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

		var newCompetitor = $(compiledTmpl).appendTo(person);

		competitorMap[newCompetitor.attr('id').replace(/\D/g,'')] = person.attr('id').replace(/\D/g,'');

		$("#id_competitorMap").attr('value', JSON.stringify(competitorMap));

		$('#id_competitor_set-TOTAL_FORMS').attr('value', count + 1);

    	new_tour_id = '#id_competitor_set-' + count.toString() + '-tour';

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

	addPerson();

	$("#right").on('click', '.add-person', function(){
	    addPerson();
	});
    
    $("#right").on("click", ".remove_person", function(e){ //user click on remove text
    	e.preventDefault(); 

        $(this).parent('div').hide();
        $(this).parent().find('input[id*="DELETE"]').prop('checked', true);

        var parent_id = $(this).parent().attr('id').replace(/\D/g,'');
        var competitorMap = JSON.parse($("#id_competitorMap").val());
		for(var f in competitorMap) {
	        if(competitorMap[f] == parent_id) {
	            delete competitorMap[f];
	        }
	    }
        $("#id_competitorMap").attr('value', JSON.stringify(competitorMap));
    });


    $("#right").on("click", ".add-competitor", function(ev){
    	ev.preventDefault();

    	var parent = $(this).parent();
    	addCompetitor(parent); //person div
    });

    $("#right").on("change", 'select[id*="birth_year"]', function(){ 

    	var person = $(this).parent().attr('id');

    	person_competitors = '#' + person + ' .competitor_div';

    	$(person_competitors).each(
    		function(index) {
    			tour_id = $(this).find('select').attr('id');
    			tour_id = '#' + tour_id;
                console.log(tour_id);
    			filterTours(tour_id);
    		});
    });

    $("#right").on("change", 'select[id*="gender"]', function(){ 

    	var person = $(this).parent().attr('id');

    	person_competitors = '#' + person + ' .competitor_div';

    	$(person_competitors).each(
    		function(index) {
    			tour_id = $(this).find('select').attr('id');
    			tour_id = '#' + tour_id;
    			filterTours(tour_id);
    		});
    });	    
});
