/* Ubuntu Server Manager
 * Copyright (C) 2007, 2008, 2009 usmteam
 * 
 * This file is part of Ubuntu Server Manager 
 * 
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 * 
*/

var tstvalidate = new valdata();

(function($){
	//mycustom function
	$.fn.myVal = function(options){
		//default values which can be change by the options parameter
		var defaults = {
			cssGreen: "valOk",			//success style
			cssAmber: "valWarn",	//warning style
			cssRed: "valError",		//error style
			cssLabelGreen:"valLabelOk",
			cssLabelAmber:"valLabelWarn",
			cssLabelRed:"valLabelError",
			labelError:true,
			labelImageGreen:"valImageOk",
			labelImageAmber:"valImageWarn",
			labelImageRed:"valImageError",
			prependError:true,			//prepend html data
			debug:false,				//should we show debug info (for developers)
			classMode:false,
			inputDefaults:true,
			//blur=false,
			valNode: "title"		//xml attribute to use for validation
		};
		//not 100% sure how this works but extend jquery with my option list
		var options = $.extend(defaults, options);
		var classValidate={};
		classValidate['postcode']='';
		classValidate['date']='';
		classValidate['numeric']='n*';
		classValidate['currency']='[$&pound;]-c*';
		classValidate['phonenumber']='N*';
		classValidate['text']='t*';
		classValidate['basicpunctuation']='T*';
		classValidate['email']='e*[+]-e*@e*'

		var errorMsg=Array();
		errorMsg[0]='Match Passed';
		errorMsg[1]='Match Inserted';
		errorMsg[2]='Characters removed please check';
		errorMsg[3]='Invalid Character Detected';
		errorMsg[4]='Required Value';
		errorMsg[5]='No Match validation Failed';
		//custom function not using jquery
		var tstvalidate = new valdata();
		
		//clear any error messages
		$('.myValMsg',this).remove();
		
		
		//go through all element (all forms selected)
		return this.each(function() {
			//select any form nodes with in the selected element
			$('input,textarea,select',this).each(function(){
				//make sure we have a name attribute else ignore
				if($(this).attr('name')){
					//make sure we have a name attribute else ignore
					if($(this).attr('id')){
						var valType=null;
						var required=false;
						if(options.classMode==true){
							for(i=0;i<$(this)[0].classList.length;i++){
								if($(this)[0].classList[i]=='required'){
									required=true;
								}
									
								for(item in classValidate){
									if($(this)[0].classList[i]==item){
										valType=classValidate[item];
									}
								}
							}
						}else{
							valType=$(this).attr(options.valNode);
						}
						console.log(valType);
						if(valType){
							var result=tstvalidate.validate($(this).val(),valType,required);
							//choose the styles that need to be applyed
							if(result[0]==0){
								var css=options.cssGreen;
								var cssLabel=options.cssLabelGreen;
							}else if(result[0]==1 || result[0]==2){
								var css=options.cssAmber;
								var cssLabel=options.cssLabelAmber;
							}else{
								var css=options.cssRed;
								var cssLabel=options.cssLabelRed;
							};
							var htm='<div class="myValMsg '+css+'">';
							if(options.debug==true){
								htm+='accuracy result='+$(this).attr('id')+'<br />';
								htm+='accuracy result='+tstvalidate.matchtext[result[0]]+'<br />';
								htm+='input value='+tstvalidate.matchtext[result[0]]+'<br />';
							}
							
							htm+='result Value='+tstvalidate.matchtext[result[0]]+'('+result[1]+')<br />';
							htm+='</div>';
							if(options.labelError==true){
								$(this).parent().find('label').addClass(cssLabel);
							}
							if(options.prependError){
								$(this).parent().prepend(htm);
							}
						}else{
							if(options.prependError){
								$(this).parent().prepend('<div class="myValMsg '+options.cssRed+'" style="border:1px solid #ff0000;">missing attribute '+options.valNode+'</div>');
							}
						}
					}
				}
				
			})
		});
	}	
})(jQuery);

/*only allow number input no text
$("input").keypress(function(e){
	if( e.which!=8 && e.which!=0 && (e.which<48 || e.which>57)){
		return false;
	}
})

*/

