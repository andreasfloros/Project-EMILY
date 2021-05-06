#include <iostream>
#include <complex>
#include <cmath>

// some definitions to make our lives easier
typedef std :: complex<float> complex_float;
const float PI = 2 * asin(1);
const std :: complex<float> I = complex_float(0.0, 1.0);

// overload multiplication since this isn't provided
complex_float operator * (complex_float a, float b){
    return complex_float(a.real() * b, a.imag() * b);
}

complex_float operator * (float a, complex_float b){
    return b * a;
}

// fft will return a pointer to the DFT of the time_series array
// note that this is allocated on the heap (need to delete manually)
// time_series array must be of type complex_float
// see main for example use
complex_float * fft(complex_float * time_series, int length){
    complex_float * ans = new complex_float [length];
    if (length == 1){
        ans[0] = time_series[0];
    }
    else{
        int half_length = length / 2;
        std :: complex<float> even_series [half_length];
        std :: complex<float> odd_series [half_length];
        for (int n = 0; n < length; n++){
            if(n % 2 == 0){
                even_series[n] = time_series[n];
            }
            else{
                odd_series[n] = time_series[n];
            }
        }
        std :: complex<float> * even_ans = fft(even_series, half_length);
        std :: complex<float> * odd_ans = fft(odd_series, half_length);
        for (int n = 0; n < length; n++){
            ans[n] = even_ans[n % half_length] + exp(float(-2) * PI * I * (n / length)) * odd_ans[n % half_length];
        }
        delete [] even_ans;
        delete [] odd_ans;
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
    int length = 30;
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

