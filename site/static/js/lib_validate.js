/* Ubuntu Server Manager
 * Copyright (C) 2007, 2008, 2009, 2010, 2011 usmteam
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
var debug=true;
function consolelog(o){
	if(debug==true){
		console.log(o);
	}
}

function oc(a){
  var o = {};
  for(var i=0;i<a.length;i++)
  {
    o[a[i]]='';
  }
  return o;
}

function valueInArray(value,list){
  for(var i=0;i<list.length;i++){
    if(value==list[i]){
		return true;
	}
  }
  return false;
}

function valdata(){
	var MATCH_EXACT=0;       //0 = exact match 
    var MATCH_INSERTED=1;    //1 = inserted match, character was inserted like a space
    var MATCH_REMOVAL=2;     //2 = invalid characters removed
    var MATCH_STOPPED=3;     //3 = stoped at invalid match
    var MATCH_NULL=4;        //4 = no Value when one required
    var MATCH_FAILURE=5;     //5 = fatal error no result returned or no result passed
    
    this.matchtext=new Array(
        'MATCH_EXACT',
        'MATCH_INSERTED',
        'MATCH_REMOVAL',
        'MATCH_STOPPED',
        'MATCH_NULL',
        'MATCH_FAILURE'
        );
    
	var format_list=new Array();
    format_list["multiline"]=Array(String.fromCharCode(10),String.fromCharCode(13));
    format_list["z"]=new Array();
    
    format_list["b"]=Array('0','1'); //numeric
    format_list["o"]=Array('0','1','2','3','4','5','6','7','8'); //numeric octal
    format_list["n"]=Array('0','1','2','3','4','5','6','7','8','9'); //numeric deciaml
    format_list["N"]=Array('0','1','2','3','4','5','6','7','8','9',' '); //numeric deciaml
    format_list["c"]=new Array(',')+format_list["n"]; //decimal_number
    format_list["l"]=Array('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z');
    format_list["l"]=format_list["l"].concat(Array('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'));
    format_list["t"]=format_list["n"].concat(format_list["l"]); //alpha numeric
    format_list["a"]=format_list["t"].concat(Array('_','-','.',' '));
    format_list["T"]=format_list["t"].concat(format_list["multiline"].concat(Array('.','_','-',' ',':',",","=","\\","%",";","/","+","*","[","]","(",")","!","?")));
    format_list["e"]=format_list["t"].concat(Array('-','_','.'));
	format_list["E"]=format_list["e"].concat(Array('@','+'));
    format_list["u"]=format_list["e"].concat(Array('&','?',':','%',';'));
    format_list["f"]=format_list["e"].concat(Array('/'));
    format_list["F"]=format_list["f"]+('\\','\n');
    format_list["D"]=format_list["e"]+("-",":","/");
    format_list["d"]=format_list["n"].concat(Array('.'));
    format_list["h"]=format_list["n"].concat(Array('a','b','c','d','e','f','A','B','C','D','E','F'));
    format_list["s"]=Array('.',',',':','|');
    format_list["p"]=Array('.',',',':','|');
	format_list["m"]=format_list["n"].concat(Array('.','£','$'));
	/*this.reset = inputClearDefaultValue;
	this.inputSetDefaultValue = inputSetDefaultValue;
	this.inputTmpValues = inputTmpValues;*/

	this.text="";
	this.textpos=0;
	this.textlen=0;


	this.format="";
	this.formatpos=0;
	this.formatchar="";
	this.formatlen=0;
	
	this.match=0;
	this.valid=true;
	
	this.reset = reset;
	this.validate = validate;
	this.handle_data = handle_data;
	this.make_list = make_list;
	this.format_pos_increment = format_pos_increment;
	this.text_pos_increment = text_pos_increment;
	this.validate_character = validate_character;
	this.get_number = get_number;
	this.validate_list=validate_list;
	this.loopmatch = loopmatch;
	this.optionalmatch = optionalmatch;
	this.countmatch = countmatch;
	this.seperator = seperator;
	this.charmatch = charmatch;
	
	function reset(){
        this.text="";
        this.textpos=0;
        this.textlen=0;
        
        this.format="";
        this.formatpos=0;
        this.formatchar="";
        this.formatlen=0;
        
        this.valid=true;
        this.match=0;
	}
	
	function validate(text,format,required){ //#text,format expected,required?
        this.reset();
        this.text=text;
        this.textlen=text.length; //len(text);
        if (format==null)
            format="t*";
        this.formatlen=format.length-1; //len(format)-1;
        this.format=format;
        this.formatchar=format.charAt(0);
        var result="";
        
		consolelog('**************** format='+format+' value='+text);
		while (this.formatchar!="" && this.textpos<this.textlen){ //:
			if (this.format.charAt(this.formatpos)=="["){
				this.make_list();
			}

			if (this.format.charAt(this.formatpos) in format_list) {
				result+=this.handle_data();
				consolelog('#'+this.format.charAt(this.formatpos));
			}else{
				result+=this.validate_list(format.slice(this.formatpos),Array(this.formatchar));
			}
		}

		consolelog('result='+result);

        /*#how accurate was the match 
        #0 = exact match 
        #1 = inserted match, character was inserted like a space
        #2 = invalid characters removed
        #3 = stoped at invalid match missing expected character, or validation string not finished incomplete
        #4 = no Value when one required
        #5 = insecure
        #6 = too short
        #<10=fatal error no result returned or no result passed
        */
        
        
        result_length=result.length; //len(result);

        
        //:#empty fields not allowed so return an error message   
        //handle this occurance first if everything is fine match will be 0 
        if (required==true){ 
            if (result_length==0){
                this.match=10;}
            if (this.textlen==0){
                this.match=4;}
        }

		if(this.match==0){
         //:#empty fields allowed so dont return error
            //#print "empty fields allowed"
            if (result==this.text){ //:#result exactly matched input 100% match
				consolelog('exact match');
                this.match=0;
            }else{
				consolelog('not exact match');
                this.match=2;
			}
		}
		
		if(this.match==0){
			if (result_length>0){ //:
				this.match=2;}
			if (result==this.text){ //:#result exactly matched input 100% match
				this.match=0;}
		}
		
		//final test if one of the required matches failed check now and set result
		//if(this.valid==false || this.formatchar){
		//	this.match=3;
		//}
		
        //#print str(this.match)+"="+this.text
        return [this.match,result,this.text];
	}
	
	//get data using list of values
    function handle_data(){
        var result="";
		
        if (format_list[this.format.charAt(this.formatpos)]=='p'){
            if (this.textlen>5){
                result+=this.validate_list(this.format.slice(this.formatpos),this.alpha_simple);
            }else{
                this.textpos=this.textlen+1;
			}
        }else{
			consolelog('handle_data letter ='+this.format[this.formatpos]);
			consolelog('format='+format_list[this.format[this.formatpos]]);
            result+=this.validate_list(this.format.charAt(this.formatpos),format_list[this.format.charAt(this.formatpos)]);
			consolelog('handle_data result ='+result);
		}
        return result;
	}

    function make_list(self){
        custom="";
        startpos=this.formatpos;
        pos=this.formatpos+1;
        tmp_format_pos=this.formatpos;
		
		
		format_list["z"]=new Array();
		consolelog('creating custom list');
        while (pos<this.formatlen && this.format[pos]!=']'){
			consolelog('add'+this.format[pos]);
            if (format_list[this.format[pos]]){
				format_list["z"].push(format_list[this.format[pos]]);
            }else{
				format_list["z"].push(this.format[pos]);
			}
            pos+=1
		}
		//this.format_pos_increment();
        pos+=1
        consolelog('resulting custom list='+format_list['z']);
        this.format=this.format.slice(0,startpos)+"z"+this.format.slice(pos);
        this.formatpos=startpos;
        this.formatlen=this.format.length-1;
        this.formatchar='z';
        consolelog('make list format pos = '+this.format[this.formatpos]);
	}

	function format_pos_increment(){
        if (this.formatpos<this.format.length){ 
            this.formatpos+=1;
            this.formatchar=this.format.charAt(this.formatpos);
        }else{
            this.formatchar="";
		}
	}
	
    function text_pos_increment(){
        if (this.textpos<this.textlen){
            this.textpos+=1;
		}
	}

    function validate_character(){
        result="";
        if (this.formatchar==this.text.charAt(this.textpos)){
            result+=this.text.charAt(this.textpos);
            this.text_pos_increment();
		}
        this.format_pos_increment();
        return result;
	}

    function get_number(){
        n="";
        while (this.formatchar in format_list['n']){
            n+=this.formatchar;
            this.format_pos_increment();
		}
        this.formatpos-=1;
        if (n == ""){
            n="0";
		}
        consolelog('character count limit = '+n);
        return parseInt(n);
	}
    
    // # type of match
    function validate_list(format,list){ //#validate a list of values
        result="";
        consolelog('**************** validate_list *****************');
        consolelog('validate_list format char before ='+this.format[this.formatpos]);
        this.format_pos_increment();
        consolelog('validate_list format char after ='+this.format[this.formatpos]);

        consolelog('validate result before ='+this.text.slice(0,this.textpos));
        if (this.textpos<this.textlen){
			//match unspecified number of matches
            if (this.formatchar=="*"){
				consolelog('validate_list loopmatch ='+this.format[this.formatpos]);
                result+=this.loopmatch(list);
            //optional match not required
            }else if (this.formatchar=="-"){
				consolelog('validate_list optionalmatch ='+this.format[this.formatpos]);
                result+=this.optionalmatch(list);
            }else if (this.formatchar in format_list['n']){
				consolelog('validate_list countmatch ='+this.format[this.formatpos]);
                result+=this.countmatch(list,this.get_number());
            }else{          
				consolelog(list+'validate_list singlematch ='+this.format[this.formatpos]);
                result+=this.charmatch(list);
                consolelog('@'+result);
			}
		}
		consolelog('validate result after ='+this.text.slice(0,this.textpos));
        return result;
	}
    
    function loopmatch(list){
        result="";
        match=true;
		
		for (var pos=this.textpos;pos<=this.textlen;pos=pos+1){
            if (match==true){   
				if (valueInArray(this.text.charAt(pos),list)){
                    result+=this.text.charAt(this.textpos);
                    this.text_pos_increment();
                }else{
                    match=false;
				}
			}
		}
        this.format_pos_increment();
        return result;
    }
    
    function optionalmatch(list){
        result="";
        
        consolelog(this.format[this.formatpos]+'optional match list= '+list);	
        consolelog(this.format[this.formatpos]+'optional match char before= '+this.formatchar);	
		if (valueInArray(this.text.charAt(this.textpos),list)){
			result+=this.text.charAt(this.textpos);
			this.text_pos_increment();
		}
		this.format_pos_increment(); 
		consolelog(this.format);
		consolelog(this.format[this.formatpos]+'optional match char after = '+this.formatchar);	
        return result;
    }
	
	function inArray(value,list){
		var result=false;
		for (item in list){
			
		}
	}

	//number of expect matches
    function countmatch(list,size){
        var result="";
        var match=true;
		consolelog('count match list ='+list);
		countlength=this.text.length-this.textpos;
		consolelog(countlength+'__'+size);
        if (countlength>size){
            countlength=size;}
        //#loop the specified number of charcter, or less if less characters exist
        consolelog('countlength'+countlength);
        consolelog('start pos'+this.textpos)
        stopPos=(this.textpos+countlength);
		for(var pos=this.textpos;pos<stopPos;pos=pos+1){
            if (match==true){                     //#loop while still correct datatype
                if (valueInArray(this.text.charAt(pos),list)){      //#is this letter in the match list
                    result+=this.text.charAt(pos);      //#build up the return value
                    this.text_pos_increment();   //#move to next character
                }else{                           //#not in match list so stop matching
                    match=false;                 //#this character stopped matching move to next value
				}
			}
		}
        this.format_pos_increment();             //#move to next formatting character
        return result;
	}
    
    function seperator(let){
        result="";
        this.format_pos_increment();
        if (!(let in this.alpha_numeric)) {
            result=this.formatchar;
            this.text_pos_increment();
            this.format_pos_increment();
		}
        return result;
    }
	
	//char match should be strict and force validation to fail if it does not match
    function charmatch(list){
		result="";
		consolelog('charmatch='+this.text.charAt(this.textpos)+'='+list);
        if (valueInArray(this.text.charAt(this.textpos), list)){
            result=this.text.charAt(this.textpos);
            this.text_pos_increment();
			consolelog('charmatch result =================================='+result);
        }else{
			consolelog('charmatch failed===============================================================');
			this.valid=false;
		}
		//this.format_pos_increment();
		return result;
	}
	
}
