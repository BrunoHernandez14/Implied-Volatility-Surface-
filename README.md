# Implied-Volatility-Surface-
This project will use the Black-Scholes Model to create a 3D surface of Implied Volatility using Brent's Method to calculate the IV values for a range of Strike Prices and Times of Expiration. I used real time market data gathered from yahoo finance and use streamlit and plotly to display everything on a webpage. With those parameters I was also able to calculate Greek derivative values and make them display on the hoverboard. 

![Alt text](IVSurfacePlot.png)

This photo illustrates the IV Surface for a SPY Call Option with a risk free rate of 5 percent and a 2 percent dividend yield with a Min Strike of 535.22 and a Max Strike of 802.84. 

How this is works is by gathering inputted parameters from the streamlit web application into the black_scholes.py file and then plotting the matrix onto the webpage after all calculations take place. 
There is a seperate file called thegreeks.py that using the same parameters calculates the Delta, Gamma, Theta, Vega, and Rho for all derivative values within the Time and Strike range. 

## What is the Black-Scholes Model? 
The Black-Scholes Model is formula used to price options with it comprising of three parts: 
1. The expected benefit from recieving the stock
2. the present value of paying/receiving the strike at expiry
3. risk neutral probability the option expires in the money

### Black-Scholes Call Formula 
$$C = S_0 \cdot N(d_1) - K e^{-rT} \cdot N(d_2)$$
### Black-Scholes Put Formula 
$$P = K e^{-rT} \cdot N(-d_2) - S_0 \cdot N(-d_1)$$

$$d_1 = \frac{\ln\left(\frac{S_0}{K}\right) + \left(r + \frac{\sigma^2}{2}\right)T}{\sigma\sqrt{T}}$$
$$d_2 = d_1 - \sigma\sqrt{T}$$

Problem is this only tells us price how do we find IV? 
We use Brent's Method which combines bisection, root bracketing, and inverse quadratic 
interpolation to find roots of a function reliably and efficiently.

### Brent's Method 
These are the three components of Brent's Method 
### 1. Root Bracketing
The algorithm requires the root to be in the interval [a,b]

$$f(a) \cdot f(b) < 0$$
### 2. Bisection 
The division of a given curve into two halves with it continuously happening until a desired accuracy is reached. 

$$s = \frac{a + b}{2}$$

### 3. Inverse Quadratic Interpolation 
Fits a quadratic through three points a,b,c and interpolates once it hits zero. 

$$s = \frac{af(b)f(c)}{(f(a)-f(b))(f(a)-f(c))} + \frac{bf(a)f(c)}{(f(b)-f(a))(f(b)-f(c))} + \frac{cf(a)f(b)}{(f(c)-f(a))(f(c)-f(b))}$$

### How they work together: 
$$\text{Use IQI if:} \quad s \in [a, b] \quad \text{and convergence is fast}$$
$$\text{Otherwise:} \quad s = \frac{a+b}{2} \quad \text{(bisection)}$$
After computing the brackets s, the bracket is updated by checking the signal 
$$\text{If } f(a) \cdot f(s) < 0 \Rightarrow b = s$$
$$\text{If } f(b) \cdot f(s) < 0 \Rightarrow a = s$$
This allows the root to always be bracketed and has to follow the Convergence Condition 
The algorithm stops when the bracket is smaller than the tolerance $\delta$
or the function evaluates to zero exactly
$$|b - a| < \delta \quad \text{or} \quad f(b) = 0$$

### The Greeks 
Greek values measure the sensitivty of the options price to multiple factors 
<img width="480" height="424" alt="image" src="https://github.com/user-attachments/assets/cc0b44d2-4d8a-4806-8e60-3f979de1dfa2" />

### Delta 
