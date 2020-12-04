% pluck a chord, dependent on pluck_func.m & non_linear.m

function y_sum = pluck_chord(freqs, dur, velo, tone, gain, dist)
fs = 44100;
y_sum = zeros(1, round(dur * fs));

for i=1:length(freqs)
    freq = freqs(i);
    % synthesize each note
    y = pluck_func(freq, dur, velo, tone, 1);
    % sum all notes
    y_sum = y_sum + y;
end

y_sum = y_sum/max(abs(y_sum));
if dist
    y_sum = y_sum * gain;
    y_sum = non_linear(y_sum);
end

end
