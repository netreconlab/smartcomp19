import numpy as np
import sim


from scipy.stats import truncnorm

np.random.seed(sim.seed)

def normal_dist(mean, sd, n=None) :
    # mu - mean
    # sigma - stardard deviation,
    # n - sample size
    #returns ndarray

    return np.random.normal(mean, sd, n)


def trunc_normal_dist(mean, sd, low, upp, n=1):
    x =  truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
    return x.rvs(n)
    #return x


def poisson_dist(lamda, n):
    # lam  - lamda
    # n - sample size
    # returns ndarray

    return np.random.poisson(lamda, n)

def exponential_dist(beta, n):
    # beta  - 1/lamda
    # n - sample size
    # returns ndarray
    return np.random.exponential(beta, n)


def uniform_dist(low, high, n):
    #low and high in floats
    # returns ndarray
    return np.random.uniform(low, high, n)


def random_int(low, high=None, size=None):
    return np.random.randint(low, high+1, size, dtype='l')


def get_rider_distribution(num = 11):
    from sklearn.preprocessing import normalize

    points = np.linspace(0, 6, num=num, endpoint=True)
    freq_dist = []

    for x in points:
        y = 0.0052*(x**3) - 0.0272*(x**2) + (0.0893*x) + 0.01
        freq_dist.append(round(y,3))

    #freq_dist[:-1] = freq_dist[:-1] + (1-sum(freq_dist))

    #freq_dist = freq_dist / np.linalg.norm(freq_dist)
    freq_dist = freq_dist / np.linalg.norm(freq_dist, ord=1)
    #print
    #np.all(norm1 == norm2)
    #print(freq_dist)

    return points,freq_dist

