import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras import backend as K

def sampling(args):
    """Reparameterization function by sampling from an isotropic unit Gaussian.
    # Arguments:
        args (tensor): mean and log of variance of Q(z|X)
    # Returns:
        z (tensor): sampled latent vector
    """

    z_mean, z_log_var = args
    batch = K.shape(z_mean)[0]
    dim = K.int_shape(z_mean)[1]
    # by default, random_normal has mean=0 and std=1.0
    epsilon = K.random_normal(shape=(batch, dim))
    return z_mean + K.exp(0.5 * z_log_var) * epsilon


def build_vae(x_shape, z_dimension):
    inputs = layers.Input(shape=x_shape)
    
    y = layers.Conv2D(32, 3, strides=2, padding="same")(inputs)
    y = layers.LeakyReLU()(y)
    y = layers.Conv2D(32, 3, strides=2, padding="same")(y)
    y = layers.LeakyReLU()(y)
    y = layers.Conv2D(32, 3, strides=2, padding="same")(y)
    y = layers.LeakyReLU()(y)
    #y = layers.Conv2D(32, 3, strides=2, padding="same")(y)
    #y = layers.LeakyReLU()(y)
    y = layers.Conv2D(32, 3, strides=2, padding="same")(y)
    y = layers.LeakyReLU()(y)
    y_shape = y.shape
    
    y = layers.Flatten()(y)
    y = layers.Dense(1024, activation='relu')(y)
    y = layers.Dense(1024, activation='relu')(y)
    
    z_mean = layers.Dense(z_dimension, name="z_mean")(y)
    z_log_var = layers.Dense(z_dimension, name="z_log_var")(y)
    z = layers.Lambda(sampling)([z_mean, z_log_var])

    decoder_input = layers.Input(shape=(z_dimension,))

    y = layers.Dense(1024, activation='relu')(decoder_input)
    y = layers.Dense(1024, activation='relu')(y)
    y = layers.Dense(y_shape[1]*y_shape[2]*y_shape[3], activation="relu")(y)
    y = layers.Reshape(y_shape[1:])(y)
    
    y = layers.Conv2DTranspose(32, 3, strides=2, padding="same")(y)
    y = layers.LeakyReLU()(y)
    y = layers.Conv2DTranspose(32, 3, strides=2, padding="same")(y)
    y = layers.LeakyReLU()(y)
    #y = layers.Conv2DTranspose(32, 3, strides=2, padding="same")(y)
    #y = layers.LeakyReLU()(y)
    y = layers.Conv2DTranspose(32, 3, strides=2, padding="same")(y)
    y = layers.LeakyReLU()(y)
    y = layers.Conv2DTranspose(x_shape[2], 3, strides=2, padding="same")(y)
    y = layers.Activation('sigmoid')(y)

    encoder = models.Model(inputs, [z_mean, z_log_var, z], name ='encoder')
    decoder = models.Model(decoder_input, y, name='decoder')
    outputs = decoder(encoder(inputs)[2])
    vae = models.Model(inputs, outputs, name = 'vae')

    return encoder, decoder, vae
import argparse

def main():
    
    opt = argparse.ArgumentParser()
    opt.add_argument('--x',  dest='x_size',type=int, default= 64, required=False, help='Input data shape. ex) 64')
    opt.add_argument('--z',  dest='z_dim', type=int, default=100, required=False, help='Latent space dimension. ex) 100' )
    argv = opt.parse_args()
    
    encoder, decoder, vae = build_vae((argv.x_size, argv.x_size, 3), argv.z_dim)
    
    encoder.summary()
    decoder.summary()
    vae.summary()

if __name__ == '__main__':
    main()
