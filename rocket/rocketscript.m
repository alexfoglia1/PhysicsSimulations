%---- DEFINISCO LE COSTANTI -----
G = 6.67*1e-11;
g = -9.81;
Mt = 6e24;
a = (-G*Mt);
Mr = 12000; %12000kg di parti meccaniche
Mc = 7000; %7000kg di carburante
c = Mr + Mc;
k = 200; %150kg al secondo
u = 2e6; %200000 m/s = 2km/s
%GFIELD_LIMIT = 5.64e7;
tmax = 150; %studio il moto tra t = 0 e t = tmax
dt = 1;
tspan = linspace(0, tmax, tmax/dt);
earth_radius = 6.371e6;

%---- DEFINISCO LE CONDIZIONI INIZIALI -----
y0 = earth_radius;
v0 = 0;
init_cond = [y0 v0];

%---- RISOLVO L'EQUAZIONE NUMERICAMENTE ----
[t,y] = ode45(@(t,y) rocket(t,y,u,a,c,k), tspan, init_cond);
[t,ideal] = ode45(@(t,y) rocket(t,y,u,0,c,k), tspan, init_cond);
real_acc = zeros(1, length(tspan));
id_acc = zeros(1, length(tspan));
real_acc(1) = 0;
id_acc(1) = 0;
for i=2:length(tspan)
  real_acc(i) = (-y(i-1,2) + y(i,2))/dt;
  id_acc(i) = (-ideal(i-1,2) + ideal(i, 2))/dt;
endfor
real_acc(1) = real_acc(2);
id_acc(1) = id_acc(2);
g_estimate = [real_acc - id_acc];
plot(t,y(:,1),'.-','DisplayName','y(t)');
hold on;
%line ("xdata",[0,tmax], "ydata",[GFIELD_LIMIT,GFIELD_LIMIT], "linewidth", 1);

%---- RISOLVO IL MOTO CON ASSUNZIONE DI G COSTANTE
v = zeros(1,length(tspan));
p = zeros(1,length(tspan));
v(1) = v0;
p(1) = y0;
mi = c + Mr;
%outOfGField = false;
for i=2:length(tspan)
  dm = k * dt;
  if (mi - dm) < Mc %se non posso bruciare dm kg di carburante:
    %disp('Carburante finito a istante');
    %input(num2str(i));
    dm = 0; %non brucio carburante
  end
  mf = mi - dm;
  %disp(['fuel: ', num2str(mf - Mr)])
  logratio = log(mi/mf);
  %if outOfGField
    %v(i) = v(i-1) + g*dt + u*logratio;
  %else
    v(i) = v(i-1) + g*dt + u*logratio;
  %end
  mi = mf;
  p(i) = p(i-1) + dt*v(i); %Eulero esplicito in avanti
  %if p(i) >= GFIELD_LIMIT
    %outOfGField = true;
  %end
end
plot(tspan,p,'.-', 'DisplayName', 'y(t) (g constant)');
legend('location', 'southeast');
figure();
plot(tspan, y(:,2), '.-');
hold on;
plot(tspan,v,'.-');
legend('v(t)', "v(t) (g constant)");
%figure();
%plot(y(:,1), g_estimate);
%grid on;
%hold on;
%legend('estimation of g', 'location', 'southeast');