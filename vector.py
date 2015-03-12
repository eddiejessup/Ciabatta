import numpy as np


def vector_mag_sq(v):
    '''
    Return the squared magnitude of vectors v.

    Parameters
    ----------
    v: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    mag: array, shape (a1, a2, ...)
        Vector squared magnitudes
    '''
    return np.square(v).sum(axis=-1)


def vector_mag(v):
    '''
    Return the magnitude of vectors v.

    Parameters
    ----------
    v: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    mag: array, shape (a1, a2, ...)
        Vector magnitudes
    '''
    return np.sqrt(vector_mag_sq(v))


def vector_unit_nonull(v):
    '''
    Return unit vectors of input vectors.
    Any null vectors in v raise an Exception

    Parameters
    ----------
    v: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    v_new: array, shape of v
    '''
    if v.size == 0:
        return v
    return v / vector_mag(v)[..., np.newaxis]


def vector_unit_nullnull(v):
    '''
    Return unit vectors of input vectors.
    Any null vectors in v are mapped again to null vectors.

    Parameters
    ----------
    v: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    v_new: array, shape of v
    '''
    if v.size == 0:
        return v
    mag = vector_mag(v)
    v_new = v.copy()
    v_new[mag > 0.0] /= mag[mag > 0.0][..., np.newaxis]
    return v_new


def vector_unit_nullrand(v):
    '''
    Return unit vectors of input vectors.
    Any null vectors in v are mapped to randomly picked unit vectors.

    Parameters
    ----------
    v: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    v_new: array, shape of v
    '''
    if v.size == 0:
        return v
    mag = vector_mag(v)
    v_new = v.copy()
    v_new[mag == 0.0] = sphere_pick(v.shape[-1], (mag == 0.0).sum())
    v_new[mag > 0.0] /= mag[mag > 0.0][..., np.newaxis]
    return v_new


def vector_angle(a, b):
    '''
    Return angles between two sets of vectors.

    Parameters
    ----------
    a, b: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    theta: array, shape (a1, a2, ...)
        Angles between a and b.
    '''
    cos_theta = np.sum(a * b, -1) / (vector_mag(a) * vector_mag(b))
    theta = np.empty_like(cos_theta)
    try:
        theta[np.abs(cos_theta) <= 1.0] = np.arccos(
            cos_theta[np.abs(cos_theta) <= 1.0])
    except IndexError:
        if np.abs(cos_theta) <= 1.0:
            theta = np.arccos(cos_theta)
        elif np.dot(a, b) > 0.0:
            theta = 0.0
        else:
            theta = np.pi
    else:
        for i in np.where(np.abs(cos_theta) > 1.0)[0]:
            if np.dot(a[i], b[i]) > 0.0:
                theta[i] = 0.0
            else:
                theta[i] = np.pi
    return theta


def vector_perp(v):
    '''
    Return vectors perpendicular to 2-dimensional vectors.
    If an input vector has components (x, y), the output vector has
    components (x, -y).

    Parameters
    ----------
    v: array, shape (a1, a2, ..., 2)

    Returns
    -------
    v_perp: array, shape of v
    '''
    if v.shape[-1] != 2:
        raise Exception('Can only define a unique perpendicular vector in 2d')
    v_perp = np.empty_like(v)
    v_perp[..., 0] = v[:, 1]
    v_perp[..., 1] = -v[:, 0]
    return v_perp


# Coordinate system transformations

def polar_to_cart(arr_p):
    '''
    Convert and return polar vectors in their cartesian representation.

    Parameters
    ----------
    arr_p: array, shape (a1, a2, ..., d)
        Polar vectors, with last axis indexing the dimension,
        using (radius, inclination, azimuth) convention.

    Returns
    -------
    arr_c: array, shape of arr_p
        Cartesian vectors.
    '''
    if arr_p.shape[-1] == 1:
        arr_c = arr_p.copy()
    elif arr_p.shape[-1] == 2:
        arr_c = np.empty_like(arr_p)
        arr_c[..., 0] = arr_p[..., 0] * np.cos(arr_p[..., 1])
        arr_c[..., 1] = arr_p[..., 0] * np.sin(arr_p[..., 1])
    elif arr_p.shape[-1] == 3:
        arr_c = np.empty_like(arr_p)
        arr_c[..., 0] = arr_p[..., 0] * np.sin(
            arr_p[..., 1]) * np.cos(arr_p[..., 2])
        arr_c[..., 1] = arr_p[..., 0] * np.sin(
            arr_p[..., 1]) * np.sin(arr_p[..., 2])
        arr_c[..., 2] = arr_p[..., 0] * np.cos(arr_p[..., 1])
    else:
        raise Exception('Invalid vector for polar representation')
    return arr_c


def cart_to_polar(arr_c):
    '''
    Convert and return cartesian vectors in their polar representation.

    Parameters
    ----------
    arr_c: array, shape (a1, a2, ..., d)
        Cartesian vectors, with last axis indexing the dimension.

    Returns
    -------
    arr_p: array, shape of arr_c
        Polar vectors, using (radius, inclination, azimuth) convention.
    '''
    if arr_c.shape[-1] == 1:
        arr_p = arr_c.copy()
    elif arr_c.shape[-1] == 2:
        arr_p = np.empty_like(arr_c)
        arr_p[..., 0] = vector_mag(arr_c)
        arr_p[..., 1] = np.arctan2(arr_c[..., 1], arr_c[..., 0])
    elif arr_c.shape[-1] == 3:
        arr_p = np.empty_like(arr_c)
        arr_p[..., 0] = vector_mag(arr_c)
        arr_p[..., 1] = np.arccos(arr_c[..., 2] / arr_p[..., 0])
        arr_p[..., 2] = np.arctan2(arr_c[..., 1], arr_c[..., 0])
    else:
        raise Exception('Invalid vector for polar representation')
    return arr_p


def sphere_pick_polar(d, n=1):
    '''
    Return polar vectors randomly picked on the unit n-sphere.

    Parameters
    ----------
    d: float
        Dimensionality of the sphere.
    n: integer
        Number of samples to pick.

    Returns
    -------
    r: array, shape (n, d)
        Sample vectors.
    '''
    a = np.empty([n, d])
    if d == 1:
        a[:, 0] = np.random.randint(2, size=n) * 2 - 1
    elif d == 2:
        a[:, 0] = 1.0
        a[:, 1] = np.random.uniform(-np.pi, +np.pi, n)
    elif d == 3:
        u, v = np.random.uniform(0.0, 1.0, (2, n))
        a[:, 0] = 1.0
        a[:, 1] = np.arccos(2.0 * v - 1.0)
        a[:, 2] = 2.0 * np.pi * u
    else:
        raise Exception('Invalid vector for polar representation')
    return a


def sphere_pick(d, n=1):
    '''
    Return cartesian vectors randomly picked on the unit n-sphere.

    Parameters
    ----------
    d: float
        Dimensionality of the sphere.
    n: integer
        Number of samples to pick.

    Returns
    -------
    r: array, shape (n, d)
        Sample cartesian vectors.
    '''
    return polar_to_cart(sphere_pick_polar(d, n))


def disk_pick_polar(n=1):
    '''
    Return polar vectors randomly picked on the 2-dimensional unit disk.

    Parameters
    ----------
    n: integer
        Number of samples to pick.

    Returns
    -------
    r: array, shape (n, 2)
        Sample vectors.
    '''
    a = np.zeros([n, 2], dtype=np.float)
    a[:, 0] = np.sqrt(np.random.uniform(size=n))
    a[:, 1] = np.random.uniform(0.0, 2.0 * np.pi, size=n)
    return a


def disk_pick(n=1):
    '''
    Return cartesian vectors randomly picked on the 2-dimensional unit disk.

    Parameters
    ----------
    n: integer
        Number of samples to pick.

    Returns
    -------
    r: array, shape (n, 2)
        Sample vectors.
    '''
    return polar_to_cart(disk_pick_polar(n))