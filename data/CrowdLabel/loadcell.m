function [lc,dflag,dattype]=loadcell(fname,delim,exclusions,varargin);
%loadcell - load various data types into a cell array.
%function [lc,dflag,numdata] = loadcell(fname, delim, exclusions, options);
%  
%  loadcell loads a cell array with character delimited
%  data, which can have variable length lines and content.
%  Numeric values are converted from string to double 
%  unless options is a string containing 'string'.
%  
%  loadcell is for use with small datasets. It is not optimised
%  for large datasets.
% 
%  FNAME is the filename to be loaded
%
%  DELIM is a string containing the relevant delimiter(s). If char(10) 
%  is included newlines are simply treated as delimiters and a 1-d array 
%  is created.
%
%  EXCLUSIONS  are the set of characters to be treated as paired
%    braces: line ends or delimiters within braces are ignored.
%    braces are single characters and any brace can pair with 
%    any other brace: no type pair checking is currently done.
%
%  OPTIONS is an options string, and can be omitted or can contain 'string'
%    if no numeric conversion is required, 'single' if multiple adjacent 
%    seperators should not be treated as one, 'free' if all linefeeds 
%    should be stripped first and 'empty2num' if empty fields are to be 
%    treated as numeric  zeros rather than an empty character set. 
%    Combine options using string concatenation.
%
%  LC is a cell array containing the loaded data.
%
%  DFLAG is a set of flags denoting the (i,j) values where data was entered
%  dflag(i,j)=1 implies lc(i,j) was loaded from the data, and not just set
%  to empty, say, by default.
%
%  NUMDATA is an array of the numeric data. numdata(i,j)=NaN implies
%    lc(i,j) is a string, otherwise it stores the number at i,j.
%    This will occur regardless of whether the 'string' option is set.
%
%  lc will return -1 if the file is not found or could not be
%  opened.
%
%  Hint: numdata+(1/dflag-1) provides a concise descriptor for the numeric 
%  data
%  Inf=not loaded
%  NaN=was string or empty set.
%  otherwise numeric
%
%  EXAMPLE
%
%[a,b,c]=loadcell('resultsfile',[',' char(9)],'"','single-string');
%   will load file 'resultsfile' into variable a, treating any of tab or 
%   comma as delimiters. Delimiters or carriage returns lying 
%   between two double inverted commas will be ignored. Two adjacent delimiters
%   will count twice, and all data will be kept as a string.
%
%   Note: in space-separated data 'single' would generally be omitted,
%   wheras in comma-seperated data it would be included.
%  
%   Note the exclusion characters will remain in the final data, and any data
%   contained within or containing exclusion characters will not be 
%   converted to numerics.
%
%Copyright 2002, 2010 Amos Storkey, University of Edinburgh. 

%Licensed under a WTFPL variant. Everyone is permitted to copy and 
%distribute verbatim or modified copies of this licensed document 
%in whatever form, and changing it is allowed as long as the 
%associated changes are not attributed to the current author.
%Obviously, this document comes with no warranty about 
%anything, ever, to the extent permitted by applicable law.
%

% This code is written with simplicity rather than efficiency in mind.
% MATLAB is incapable of loading variable length lines or variable type values
% with a whole file command under the standard library sets. This mfile 
% fills that gap.


numattime = 60000;
multflag = 1;
stringflag = 0;
emptnum = 0;
freeform = 0;

args = varargin;
nargs = length(args);
if (nargs>1)
 for i = 1:2:nargs
  switch args{i},
   case 'single',      multflag = 1-args{i+1};
   case 'string',      stringflag = args{i+1};
   case 'empty2num',   emptnum = args{i+1};
   case 'free',        freeform = args{i+1};
  end
 end
else
  if nargs<1
    options=' ';
  else
    options=args{1};
  end
  multflag = isempty(findstr(options,'single'));
  stringflag = ~isempty(findstr(options,'string'));
  emptnum = ~isempty(findstr(options,'empty2num'));
  freeform = ~isempty(findstr(options,'free'));
end
%Open file
fid=fopen(fname,'rt');
%Cannot open: return -1
if (fid<0)
  lc=-1;
else
  i=1;
  j=1;
  addonbeginning=[];
  notalldone=1;
  while notalldone
   [fullfile,fcount]=fread(fid,numattime,'uchar=>char');
   fullfile=[addonbeginning fullfile']; 
   notalldone=~feof(fid);
   if feof(fid)
     fullfile=[fullfile delim(1)];
   end
   %Strip LF if free is set
   if freeform
       fullfile=strrep(fullfile,char(10),'');
       fullfile=strrep(fullfile,char(13),'');
   end    
   [delimpos,endpos,xclpos,jointpos]=getdelimpos(fullfile,delim,exclusions);
    
   posind=1;
   %Run through
   getstrt=0;
   strdubt=0;
   %=====================================================================
   %If no numeric coversion do as quickly as possible
   %=====================================================================
   if stringflag
     while (posind<(length(jointpos)))
       %Get current field
       lc{i,j}=fullfile(jointpos(posind)+1:jointpos(posind+1)-1);
       dflag(i,j)=1;
       j=j+1*(~(isempty(lc{i,j}) & multflag));
       if (fullfile(jointpos(posind+1))==char(10)) | (fullfile(jointpos(posind+1)==char(13)))
          i=i+1;
          j=1;
       end;
       posind=posind+1;
     end
   %======================================================================
   %Otherwise
   %=====================================================================
   else
    while (posind<(length(jointpos)))
     %Get current field
     tempstr=fullfile(jointpos(posind)+1:jointpos(posind+1)-1);
     %If empty only continue if adjacent delim count.
     if ~(isempty(tempstr) & multflag);
       %This ij is set
       dflag(i,j)=1;
       %Convert to num if stringflag not set
       tempno=NaN;
       if ~stringflag
         %tempno=str2double([tempstr]);
         [tempno,count,dummy,nextindex]=sscanf(tempstr,'%g',1);
         if (ischar(tempno) | any(tempstr(nextindex:end)~=' ')) tempno=NaN; end;
         %tempno=1;
         %If emptystring convert to zero if emptnum set
         if (isempty(tempstr) & emptnum)
             tempno=0;
         end;
       end
       %Set dattype to no (or NaN if not a num
       dattype(i,j)=tempno;
       %If NaN set lc to string else to num if stringflag not set
       if (isnan(tempno) |  stringflag) 
         lc{i,j}=tempstr;
       else
         lc{i,j}=tempno;
       end;
      %Next j
       j=j+1;
     end;
     %If eol inc i and reset j
     if ismember(fullfile(jointpos(posind+1)),[char(10) char(13)])
         i=i+1;
         j=1;
     end;
     %Inc to next delim
     posind=posind+1;      
    end;  
   end;
   %==============================================================================
   addonbeginning=fullfile(jointpos(posind)+1:end); 
  end;   
end;
%Logicalise dflag
dflag=logical(dflag);




function [delimpos,endpos,xclpos,jointpos]=getdelimpos(fullfile,delim,exclusions);

  %Find all delimiters
   delimpos=(fullfile==delim(1));
   for s=2:length(delim)
     delimpos=(delimpos | (fullfile==delim(s)));
   end
   delimpos=find(delimpos);
  
   %Find all eol
   endpos=find(fullfile==char(10));
   if isempty(endpos)
      endpos=find(fullfile==char(13));
   end
   endpos=setdiff(endpos,delimpos);
   %find all exclusions
   xclpos=[];
   if length(exclusions)>0
    xclpos=(fullfile==exclusions(1));
    for s=2:length(exclusions);
      xclpos=[xclpos | (fullfile==exclusions(s))];
    end
    xclpos=find(xclpos);
    xclpos=[xclpos(1:2:end-1);xclpos(2:2:end)];
    %Combine eol and delimiters
   end
   jointpos=union(delimpos,endpos);
   t=1;
   %Remove delim/eol within exclusion pairs
   removedelim=[];
   if length(xclpos)>0
    for s=1:length(jointpos)
      if any((jointpos(s)>xclpos(1,:)) & (jointpos(s)<xclpos(2,:)))
        removedelim(t)=jointpos(s);
        t=t+1;
      end;
    end
    %and add start point
   end
   jointpos=[0 setdiff(jointpos,removedelim)];
