import tensorflow as tf


def downscale_local_mean(image, factors, cval=0):
    """
    Down-sample N-dimensional image by local averaging.
    The image is padded with 'cval' if it is not perfectly divisible by the integer factors.
    This function calculates the local mean of elements in each block of size 'factors' in the input image.
    Equivalent to skimage.transform.downscale_local_mean

    :param image: ndarray or tensor
        N-dimensional input image.
    :param factors: array-like
        Array containing down-sampling integer factor along each axis.
    :param cval: float, optional
        Constant padding value if image is not perfectly divisible by the integer factors.

    :return: tensor
        Down-sampled image in the format of tensor with same number of dimensions as input image.

    """

    session = tf.Session()
    # if the input is a tensor, convert it to an ndarray
    if tf.is_tensor(image):
        image = session.run(image)
    image_downscaled = block_reduce(image, factors, tf.reduce_mean, cval)

    return tf.convert_to_tensor(image_downscaled)


def block_reduce(image, block_size, func=tf.reduce_sum, cval=0):
    """
    Down-sample image by applying function to local blocks.

    :param image: ndarray
        N-dimensional input image.
    :param block_size: array-like
        Array containing down-sampling integer factor along each axis.
    :param func: callable
        Function object which is used to calculate the return value for each local block. This function must implement
        an axis parameter such as tf.reduce_sum or tf.reduce_min
    :param cval: float
        Constant padding value if image is not perfectly divisible by the block size.

    :return: ndarray
        Down-sampled image with same number of dimensions as input image.
    """
    # if the dimension of block_size and image is not the same, raise error
    if len(block_size) != image.ndim:
        raise ValueError("`block_size` must have the same length as `image.shape`.")

    # apply the pad operation on image
    pad_width = []
    for i in range(len(block_size)):
        if block_size[i] < 1:
            raise ValueError("Down-sampling factors must be >= 1.")
        if image.shape[i] % block_size[i] != 0:
            after_width = block_size[i] - (image.shape[i] % block_size[i])
        else:
            after_width = 0
        pad_width.append((0, after_width))
    image = tf.convert_to_tensor(image)
    image = tf.pad(image, pad_width, "CONSTANT")

    # compute the block view of image 
    blocked = view_as_blocks(image, block_size)
    blocked = tf.cast(blocked, tf.float64)
    session = tf.Session()
    image = session.run(image)
    blocked = session.run(blocked)
    # apply the given func on blocked
    result = func(blocked, axis=tuple(range(image.ndim, blocked.ndim)))

    return session.run(result)
