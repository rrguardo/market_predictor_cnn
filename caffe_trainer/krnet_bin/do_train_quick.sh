#!/bin/bash


caffe train --solver=cifar10_quick_solver.prototxt
caffe train --solver=cifar10_quick_solver_lr1.prototxt --snapshot=krnet_quick_iter_4000.solverstate.h5

