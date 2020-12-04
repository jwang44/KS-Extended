function a=non_linear(a)
a(a<=-1) = -2/3;
a(a>=1) = 2/3;
a(a>-1 & a<1) = a-a.^3/3;
end