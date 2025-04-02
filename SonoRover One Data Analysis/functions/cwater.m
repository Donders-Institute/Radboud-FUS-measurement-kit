function [c, rho]  = cwater(T)
%%CWATER            speed of sound in pure water as a function of temperature
%
% Function returns sound speed [m/s] given Temperature [deg C]
%
% Syntax:  c = cwater(T)
%
% Inputs:
%    T - Temperature [deg C]
%
% Outputs:
%    c - Sound Speed [m/s]
%    rho - density in kg/m3
%
% Example: 
%    c = cwater(21)
%
% See also: cwater2.m

%   Author(s): Jason Raymond; jason.lawrence.raymond@gmail.com
%   National Center for Physical Acoustics, University, MS
%   March 2007; Last revision: 23 May 2007 
%    
%   Ahthor Stein Fekkes. Added the density calcluation december 2024
%
% References:
% [1] Del Grosso, V. A. and Mader, C. W., "Speed of sound in pure water,"
% Journal of the Acoustic Society of America, vol. 52 pp. 1442-1446, 1972.
%
% [2] Bilaniuk, N. and Wong, G. S. K., "Speed of sound in pure water as a
% function of temperature," The Journal of the Acoustical Society of
% America, vol. 93(3), pp. 1609-1612, 1993. as amended by
% Bilaniuk, N. and Wong, G. S. K., "Erratum: Speed of sound in pure water 
% as a function of temperature [J. Acoust. Soc. Am. 93, 1609-1612 (1993)]," 
% The Journal of the Acoustical Society of America, vol. 99(5), p 3257.

%[1] combined fit according to t68 temperature scale 
%  [3.14643091E-9 -1.47800417E-6 3.34198834E-4 5.80852166E-2 -5.03711129E0 1.40238754E3];

%[2] combined fit according to t90 temperature scale, adopted in 1990
% [3.16585020E-9 -1.48259672E-6 3.34638117E-4 -5.81172916E-2 5.03836171E0 1.40238744E3]; 

% Density related references(according to chatGPT)
%
% Wagner and Pruß (2002):
% Wagner, W., & Pruß, A. (2002). "The IAPWS Formulation 1995 for the Thermodynamic Properties of Ordinary Water Substance for General and Scientific Use." Journal of Physical and Chemical Reference Data, 31(2), 387–535.
% 
% This is the definitive source for high-accuracy water property equations, including density, based on the International Association for the Properties of Water and Steam (IAPWS) standards.
% Weast (1984):
% Weast, R. C., & Astle, M. J. (1984). CRC Handbook of Chemistry and Physics. CRC Press.
% 
% Provides empirical data and approximations, including polynomial fits for water density across various temperatures.
% Engineering Toolbox:
% The Engineering Toolbox is a practical resource summarizing experimental data for water density across a wide range of temperatures:
% https://www.engineeringtoolbox.com/water-density-specific-weight-d_595.html
% 
% Includes tables and approximations similar to the formula provided.

  %% calculate the values at the desired temperature
  
  if (nargin==1)
    % Ref [1,2]
    k=[3.16585020E-9 -1.48259672E-6 3.34638117E-4 -5.81172916E-2 5.03836171E0 1.40238744E3];   
    c=polyval(k,T); % Sound speed [m/s]

    % Coefficients for the polynomial approximation
    a0 = 999.842594;
    a1 = 6.793952e-2;
    a2 = -9.095290e-3;
    a3 = 1.001685e-4;
    a4 = -1.120083e-6;
    a5 = 6.536332e-9;
    
    % Calculate densit
    rho = a0 + a1*T + a2*T.^2 + a3*T.^3 + a4*T.^4 + a5*T.^5;

  end

  %% no arguments given, make a plot of the function
  
  if (nargout==0 && nargin==0)
    T = 0:0.1:100;
    c = cwater(T);
    figure;
    plot(T,c);
    grid on;
    title('Speed of Sound in Pure Water');
    xlabel('Temperature (\circC)');
    ylabel('Sound speed (m/s)');
    clear c
  end
  
end  
