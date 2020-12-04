% script to load and synthesize sound using midi file
% dependent on pluck_func.m & non_linear.m
clear;close;
% use miditoolbox: https://github.com/miditoolbox/1.1
addpath("/Users/apple/Downloads/1.1-master/miditoolbox");

% read midi file, information is given in a matrix (nmat)
nmat = readmidi('dist.mid');
% onset, dur, channel, pitch, velocity, onset, dur
nmat = nmat(:, 4:7);
% pitch, velocity, onset, dur
nmat(:, 1) = midi2hz(nmat(:, 1));
% freq, velocity, onset, dur

% specify parameters
dist = true;
velocity = 1;
tone = 0.9; 
gain = 5;
fs = 44100;

% define the total output length
len = ceil((nmat(end, 3)+nmat(end, 4)+2) * fs); 
% output buffer
song = zeros(1, len);

for i=1:length(nmat)    
    % calculate parameter for each note
    freq = nmat(i, 1);
    dur = nmat(i, 4);
    velo = nmat(i, 2) / 127;  
    onset = nmat(i, 3);
    
    y = pluck_func(freq, dur*1.1, velo, tone, 1);
    
    % starting position of each note
    nbegin = max(1, round(onset * fs));
    
    % add every note to the output
    song(nbegin:nbegin+length(y)-1) = song(nbegin:nbegin+length(y)-1)+y;
end

if dist
    song = song/max(abs(song));
    song = song * gain;
    song = non_linear(song);
end

plot(song);
soundsc(song, fs);
%song = song/max(abs(song));
audiowrite('dist.wav', song, fs);
