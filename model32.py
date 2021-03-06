# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 22:14:37 2017

@author: LENOVO
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 10:41:53 2017

@author: LENOVO
"""

import tensorflow as tf
import numpy as np
import os
import scipy.io as sio  
import PIL as Image


import six

import cv2 as cv
from sklearn.feature_extraction.image import extract_patches_2d

def inference(images,batch_size,keep_prob):
#    img = cv.imread(images)
    sess = tf.Session() 
    with sess.as_default():
        images=images.eval()
        patches = extract_patches_2d(images, (32,32),32)
        X = np.transpose(patches.reshape((-1, 32, 32, 3)), (0, 3, 1, 2))
        X2 = tf.cast(X,tf.float32)
#    img1 = X2[0]
    conv = tf.placeholder(tf.float32, shape = [32,32,32,3])
    conv1 = tf.placeholder(tf.float32, shape = [32,26,26])
    with tf.variable_scope('conv1') as scope:
        weights = tf.get_variable('weights',
                                  shape = [7,7,3,50],
                                  dtype = tf.float32,
                                  initializer = tf.truncated_normal_initializer(stddev=0.1,dtype=tf.float32))
        biases = tf.get_variable('biases',
                                 shape = [50],
                                 dtype = tf.float32,
                                 initializer = tf.constant_initializer(0.1))
#==============================================================================
#         conv = tf.nn.conv2d(images, weights, strides=[1,1,1,1], padding ='VALID')
#         pre_activation = tf.nn.bias_add(conv,biases)
#         conv1 = tf.nn.relu(pre_activation, name=scope.name)
#==============================================================================
        for i in range(32):
            conv[i] = tf.nn.conv2d(X2[i], weights, strides=[1,1,1,1], padding ='VALID')
            pre_activation = tf.nn.bias_add(conv[i],biases)
            conv1[i] = tf.nn.relu(pre_activation, name=scope.name)
        
#==============================================================================
#     with tf.variable_scope('pooling_max') as scope:
#         pool1 = tf.nn.max_pool(conv1,ksize=[1,26,26,1],strides=[1,1,1,1],
#                                padding='VALID',name='pooling_max')
#         norm1 = tf.nn.lrn(pool1,depth_radius=4,bias=1.0,alpha=0.001/9.0)
#         
#     with tf.variable_scope('pooling_min') as scope:
#         pool2 = tf.nn.avg_pool(conv1,ksize=[1,26,26,1],strides=[1,1,1,1],
#                                padding='VALID',name='pooling_min')
#         norm2 = tf.nn.lrn(pool2,depth_radius=4,bias=1.0,alpha=0.001/9.0)
# 
#     pool = tf.concat(3,[norm1,norm2])
#     
#     with tf.variable_scope('local3') as scope:
#         reshape = tf.reshape(pool, shape= [batch_size, -1])
#         dim = reshape.get_shape()[1].value
#         weights = tf.get_variable('weights',
#                                   shape=[dim,400],
#                                   dtype=tf.float32,
#                                   initializer=tf.truncated_normal_initializer(stddev=0.005,dtype=tf.float32))
#         biases = tf.get_variable('biases',
#                                  shape=[400],
#                                  dtype=tf.float32,
#                                  initializer=tf.constant_initializer(0.1))
#         local3 = tf.nn.relu(tf.matmul(reshape,weights) + biases, name=scope.name)
#         
#     with tf.variable_scope('local4') as scope:
#         reshape = tf.reshape(local3, shape= [batch_size, -1])
#         weights = tf.get_variable('weights',
#                                   shape=[400,400],
#                                   dtype=tf.float32,
#                                   initializer=tf.truncated_normal_initializer(stddev=0.005,dtype=tf.float32))
#         biases = tf.get_variable('biases',
#                                  shape=[400],
#                                  dtype=tf.float32,
#                                  initializer=tf.constant_initializer(0.1))
#         local4 = tf.nn.relu(tf.matmul(reshape,weights) + biases, name='local4')
#         local4 = tf.nn.dropout(local4,keep_prob=keep_prob)
# 
# 
#     with tf.variable_scope('regression') as scope:
#         reshape = tf.reshape(local4, shape = [batch_size, -1])
#         weights = tf.get_variable('weights',
#                                   shape = [400,1],
#                                   dtype = tf.float32,
#                                   initializer=tf.truncated_normal_initializer(stddev=0.005,dtype=tf.float32))
#         biases = tf.get_variable('biases',
#                                  shape=[1],
#                                  dtype = tf.float32,
#                                  initializer=tf.constant_initializer(0.1))
#         regression = tf.nn.relu(tf.matmul(reshape,weights) + biases, name = 'regression')
#     return regression
#==============================================================================
    return conv1
    
def losses(logits, scores):
    with tf.variable_scope('loss') as scope:
#		cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits\
#		                (logits = logits, labels = scores, name = 'xentropy_per_example')
        scores = tf.cast(scores,tf.float32)
        logits = tf.reshape(logits,[256])
        loss = tf.abs(logits-scores)
        loss = tf.reduce_mean(loss, name='loss')
        tf.summary.scalar(scope.name+'/loss',loss)
    return loss

def trainning(loss):

    with tf.name_scope('optimizer'):
        start_learning_rate = 0.01
        global_step = tf.Variable(0,name = 'global_step',trainable=False)
        learning_rate = tf.train.exponential_decay(start_learning_rate,
                                                   global_step=global_step,
                                                   decay_steps=120,decay_rate=0.95)
#        optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
        tf.summary.scalar('optimizer/learning_rate',learning_rate)
        optimizer = tf.train.GradientDescentOptimizer(learning_rate = learning_rate)
        train_op = optimizer.minimize(loss, global_step = global_step)
    return train_op

def evaluation(logits, scores):

    with tf.variable_scope('error') as scope:
        logits = tf.reshape(logits,[256])
        scores = tf.cast(scores,tf.float32)
#        correct = tf.nn.in_top_k(logits,scores,1)
        correct = tf.abs(logits-scores)
        correct = tf.divide(correct,scores)
#        correct = tf.cast(correct, tf.float16)
        accuracy = tf.reduce_mean(correct)
        error = tf.multiply(accuracy,100)
        tf.summary.scalar(scope.name+'/error',error)
    return error
