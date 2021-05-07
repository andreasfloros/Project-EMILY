#include <iostream>
#include <complex>
#include <cmath>

// some definitions to make our lives easier
typedef std :: complex<float> complex_float;
const float PI = 2 * asin(1);

// overload multiplication since this isn't provided
complex_float operator * (complex_float a, float b){
    return complex_float(a.real() * b, a.imag() * b);
}

complex_float operator * (float a, complex_float b){
    return b * a;
}

unsigned int bit_reverse(unsigned int x, int log2x)
{
    int y = 0;
    for (int n = 0; n < log2x; n++)
    {
        y <<= 1;
        y |= (x & 1);
        x >>= 1;
    }
    return y;
}

// fft will return a pointer to the DFT of the time_series array
// note that this is allocated on the heap (need to delete manually)
// time_series array must be of type complex_float
// see main for example use
complex_float * fft(complex_float * time_series, int length){
    const complex_float I = complex_float(0, 1);
    complex_float * ans = new complex_float [length];
    int log2x = log2(length);
    for (unsigned int n = 0; n < length; n++){
        int rev_idx = bit_reverse(n, log2x);
        ans[n] = time_series[rev_idx]; 
    }
    for (int n = 1; n <= log2x; n++){
        int m = 1 << n;
        int m2 = m >> 1;
        complex_float w = complex_float(1, 0);
        complex_float wm = exp(I * (PI / m2));
        for (int j = 0; j < m2; j++){
            for (int k = j; k < length; k += m){
                complex_float t = w * ans[k + m2];
                complex_float u = ans[k];
                ans[k] = u + t;
                ans[k + m2] = u - t;
            }
            w *= wm;
        }
    }
    return ans;
}

// helper function to make testing easier
void print_complex_array(complex_float * array, int length){
    for (int n = 0; n < length; n++){
        std :: cout << array[n] << " ";
    }
    std :: cout << std :: endl;
    return;
}

// example call to fft
int main(){
    int length = 32;
    float time_series [length] = {1}; // kronecker delta
    complex_float complex_time_series [length];
    for (int n = 0 ; n < length; n++){
        complex_time_series[n] = time_series[n]; // convert to complex type
    }
    print_complex_array(complex_time_series, length);
    complex_float * ans = fft(complex_time_series, length);
    print_complex_array(ans, length); // result is constant, as expected
    delete [] ans; // make sure to deallocate
    return 0;
}

