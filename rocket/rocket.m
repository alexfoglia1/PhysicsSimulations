function dydt = rocket(t,y,u,a,c,k)
  dydt = zeros(2,1);
  dydt(1) = y(2); % y'(t)
  dydt(2) = u*(k/(c + k*t)) + a*(1/(y(1)^2)); % y''(t)
