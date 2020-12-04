% pluck single note
% for functionized version, see pluck_func.m
% this script makes a sound

clear; close;
% set a fixed seed so that initial timbre doesn't change
rng(1);

% parameters
f0=82; dur=5; A=1; tone=0.8; gain=1;

fs = 44100;  % sample rate

N = round( dur * fs );
y = zeros( 1, N );      % output buffer

delay = fs / f0;        % delay line length in samples
delay = delay - 1;      % subtract phase delay of averaging filter
D = floor( delay );

% c0&c1, linear interp coefficients
c1 = delay - D;
c0 = 1 - c1;

% Initialize delayline with random binary values
dl = A * round( rand( 1, D ) );
dl( dl == 0 ) = -A;
dl = dl - mean(dl);     % kill the dc
ptr = 1;


delay_fb = 0.7 * D;     % feedback delay
D_fb = floor(delay_fb);
dl_fb = zeros(1, D_fb); % feedback delay line
ptr_fb = 1;

% 3-point averaging lp parameters
a0 = 0.05; %我们需要a1>2a0,同时a1+2a0=1,a1越大，高频越多
%a1 = 0.9; % y(n)=a0*x(n)+a1*x(n-1)+a0*x(n-2)
a1 = 1 - 2*a0;

% dc-blocking parameters
dc_block_co = f0/fs/10;
dc_block_a0 = 1/(1+dc_block_co/2);
dc_block_a1 = -dc_block_a0;
dc_block_b1 = dc_block_a0 * (1 - dc_block_co/2);

% final modification parameter (tone control)
a = 1 / (2*cos(2*pi*f0/fs)+1);
% how many times initial values are passed through the lp

pass = -100 * tone + 100; % map tone(0~1) to pass(100~0)
for m = 1:pass
  % control brightness of the sound
  dl = filter([a,a,a], 1, dl);
end

xm2ave = 0; % x[n-2] for 3-point averaging lp filter
xm1ave = 0; % x[n-1] for 3-point averaging lp filter
ym1 = 0;  % y[n-1]

y_avgm1 = 0;
y_block_m1 = 0;

for n = 1:N

  x = dl(ptr);
  % 3-point averaging lp
  y_avg = a0*x + a1*xm1ave + a0*xm2ave;
  xm2ave = xm1ave;
  xm1ave = x;

  % dc-blocking
  y_block = dc_block_a0*y_avg + dc_block_a1*y_avgm1 + dc_block_b1*y_block_m1;    
  y_avgm1 = y_avg;
  y_block_m1 = y_block;

  % linear interpolation
  y(n) = c0 * y_block + c1 * ym1;
  ym1 = y_block;

  dl( ptr ) = y(n); % write back to delayline
  
  y(n) = y(n)*gain; % pre-dist gain
  % non linearity
  if y(n)>=1
    y(n)=2/3;
  elseif y(n)<=-1
    y(n)=-2/3;
  else
    y(n)=y(n)-y(n)^3/3;
  end
  
  % feedback
  dl(ptr) = dl(ptr) + dl_fb(ptr_fb);
  dl_fb(ptr_fb) = 0.01*y(n);   % output is attenuated by 0.01

  ptr = ptr + 1;
  if ( ptr > D ), ptr = 1; end
  ptr_fb = ptr_fb + 1;
  if (ptr_fb > D_fb), ptr_fb = 1; end

end
soundsc( y, fs );
