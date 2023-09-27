close all
clear
clc

%mystrings = cell(1, 12);  % Erstellen Sie einen Zell-Array, um die Dateinamen zu speichern
for number = 0:11
    mystrings{number + 1} = ['C:\Users\domin\OneDrive\Raspberry Pico\data_log_', num2str(number), '.txt'];
end

a = readtable("C:\Users\domin\OneDrive\Raspberry Pico\data_log_0.txt",'Delimiter',';');
a.datetime = datetime(a.datetime,'InputFormat','(yyyy,MM,dd,HH,mm,ss)');
a = table2timetable(a);
vec = [0;diff(a.datetime)== 0];
a = a(~vec,1:13);
min(diff(a.datetime))

for s = mystrings
    
    b = readtable(s{1},'Delimiter',';');
    b.datetime = datetime(b.datetime,'InputFormat','(yyyy,MM,dd,HH,mm,ss)');
    b = (table2timetable(b));
    vec = [0;diff(b.datetime)== 0];
    b = b(~vec,1:13);
    disp([s{1},' geladen'])
    try
        a = union(a,b);
    catch
        disp([s{1},' NICHT VEREINIGT'])

    end
end


%%
writetimetable(a,'log_data.csv','Delimiter',';')
plot(a.datetime,a.Temperatur)

%%
clc
a = readtimetable("C:\Users\domin\OneDrive\Raspberry Pico\data_log.csv",'Delimiter',';');
%%
vec = a.relay_AC_3;
change_indices = [1 ;find(diff(vec)); numel(vec)];
for i = 1:numel(change_indices)-2
    r(change_indices(i):change_indices(i+2)) = mean(vec(change_indices(i):change_indices(i+2)));
end
a.Heizung = r';
plot(a,{'Temperatur','Heizung'})


