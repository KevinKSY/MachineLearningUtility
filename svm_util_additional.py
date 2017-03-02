#!/usr/bin/env python3
import sys
import time
import datetime
import os
from svmutil import *
from shutil import copyfile
import numpy as np

def svm_make20SimModel(svmModel, xScaler, yScaler, modelName = 'SVM'):
# The funcion produces 20-sim model for the given svm model with the scalers
# input and outputs.
# arguments:
#   svmModel: svmModel from obtained using libsvm package
#   xScaler: 2d numpy array [2,:] for scaling the inputs.
#           The first row is for bias values (mean or minimum), and the
#           second row is for scaling values (standard deviation or range).
#   yScaler: a numpy array [2] for scaling the output.
#           The first element is for bias values (mean or minimum), and the
#           other is for scaling values (standard deviation or range).
#   modelName: The name of the submodel for the target 20-sim model
# output: True or False, but it saves the model by the given model name

    if not(os.path.isfile('20Sim_tmp.tmp')):
        print("The 20-sim model template file ('20Sim_tmp.tmp') missing")
        return False
    else:
        try:
            np.set_printoptions(threshold=np.inf)

            nSV = svmModel.get_nr_sv()
            SV = svmModel.get_SV()
            svCoeff = svmModel.get_sv_coef()

            textToSearch = ['%%path%%', '%%time%%', '%%modelName%%',
                            '%%noInput%%', '%%equations%%']
            pathToWrite = os.getcwd()
            timeToWrite = str(datetime.datetime.now())
            modelNameToWrite = modelName
            fileName = modelName + '.emx'
            noInput = 0
            for i in range(nSV):
                noInput = max(list(SV[i].keys())) if max(list(SV[i].keys())) > noInput else noInput
            parameters = ['parameters\n']
            parameters.append('\tinteger nSV = ' + str(nSV) + ';\n')
            Mat = np.zeros([noInput,nSV])
            for i in range(nSV):
                for j in list(SV[i]):
                    if j > 0:
                        Mat[j-1,i] = SV[i][j]
            MatText = np.array2string(Mat, separator = ',')
            MatText = MatText.replace('],',';')
            MatText = MatText.replace(']','')
            MatText = MatText.replace('[','')
            parameters.append('\treal SV[{0:d},{1:d}] = '.format(noInput, nSV) + '[' + MatText + ']' + ';\n')
            Mat = np.zeros([nSV,1])
            for i in range(nSV):
                Mat[i] = svCoeff[i][0]
            MatText = np.array2string(Mat, separator=',')
            MatText = MatText.replace('],',';')
            MatText = MatText.replace(']','')
            MatText = MatText.replace('[','')
            MatText = MatText.replace('\n','')
            parameters.append('\treal svCoeff[{0:d}] = '.format(nSV) + '[' + MatText + ']' + ';\n')
            parameters.append('\treal rho = {0:f};\n'.format(svmModel.rho[0]))
            parameters.append('\treal gamma = {0:f};\n\n'.format(svmModel.param.gamma))
            parameters.append('\treal x_data_bias[{0:d}] = '.format(noInput) + str(list(xScaler[0,:])).replace(',',';') + ';\n'.format(noInput))
            parameters.append('\treal x_data_scale[{0:d}] = '.format(noInput) + str(list(xScaler[1,:])).replace(',',';') + ';\n'.format(noInput))
            parameters.append('\treal y_data_bias =' + str(yScaler[0]) + ';\n')
            parameters.append('\treal y_data_scale =' + str(yScaler[1]) + ';\n\n')

            variables = ['variables\n']
            variables.append('\treal hidden x_scale[{0:d}], y_scale;\n'.format(noInput))
            variables.append('\tinteger i;\n\n')

            equations = ['code\n']
            equations.append('\tx_scale = (input - x_data_bias) ./ x_data_scale;\n')
            equations.append('\ty_scale = 0;\n')
            equations.append('\tfor i = 1 to nSV do\n')
            equations.append('\t\ty_scale = y_scale + svCoeff[i]*exp(-msum((SV[:,i] - x_scale).^2)*gamma);\n')
            equations.append('\tend;\n')
            equations.append('\ty_scale = y_scale - rho;\n')
            equations.append('\toutput = y_scale * y_data_scale + y_data_bias;')

            equations = ''.join(parameters) + ''.join(variables) + ''.join(equations)
            textToReplace = [pathToWrite, timeToWrite, modelNameToWrite, str(noInput), equations]

            copyfile('20Sim_tmp.tmp', fileName)

            # Read in the file
            with open(fileName, 'r') as file:
                filedata = file.read()

            # Replace the target string
            for i, textNow in enumerate(textToSearch):
                filedata = filedata.replace(textNow, textToReplace[i])

            # Write the file out again
            with open(fileName, 'w') as file:
                file.write(filedata)

            return True

        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
            return False
        except ValueError as e:
            print ("Value error: {0}".format(e))
            return False
        except TypeError as e:
            print ("Type error: {0}".format(e))
            return False
        except:
            print ("Unexpected error:", sys.exc_info()[0])
            raise


def svm_makeMFunction(svm_model, xScaler, yScaler, funcName):
# The funcion produces matlab function for the given svm model with the scalers
# input and outputs.
# arguments:
#   svmModel: svmModel from obtained using libsvm package
#   xScaler: 2d numpy array [2,:] for scaling the inputs.
#           The first row is for bias values (mean or minimum), and the
#           second row is for scaling values (standard deviation or range).
#   yScaler: a numpy array [2] for scaling the output.
#           The first element is for bias values (mean or minimum), and the
#           other is for scaling values (standard deviation or range).
#   modelName: The name of the submodel for the target 20-sim model
# output: True or False, but it saves the model by the given model name
    try:
        f = open(funcName + '.m', 'w')
        f.write('function y = ' +  funcName  + '(x)\n')
        f.write('% Automatic code generation by Kevin Koosup Yum \n')
        f.write('x_data_bias = [')
        for i in range(len(xScaler[0])):
            f.write('%f ' % xScaler[0,i])
        f.write('];\n')
        f.write('x_data_scale = [')
        for i in range(len(xScaler[1])):
            f.write('%f ' % xScaler[1,i])
        f.write('];\n')
        f.write('y_data_bias = %f;\n'  % yScaler[0])
        f.write('y_data_scale = %f;\n\n'  % yScaler[1])
        nSV = svm_model.get_nr_sv()
        f.write('nSV = %d;\n' % nSV)
        SV = svm_model.get_SV()
        f.write('SV = [')
        noInput = len(xScaler[0])
        Mat = np.zeros([nSV,noInput])
        for i in range(nSV):
            for j in list(SV[i]):
                if j > 0:
                    Mat[i,j-1] = SV[i][j]
        for i in range(nSV):
            for j in range(noInput):
                f.write('%f ' % Mat[i,j])
            f.write('; ')
        f.write('];\n')
        svCoeff = svm_model.get_sv_coef()
        f.write('svCoeff = [')
        for i in range(nSV):
            f.write('%f ' % svCoeff[i][0])
        f.write('];\n')
        f.write('rho = %f;\n' % svm_model.rho.contents.value)
        f.write('gamma = %f;\n\n' % svm_model.param.gamma)
        f.write('x_scale = bsxfun(@minus, x, x_data_bias);\n')
        f.write('x_scale = bsxfun(@rdivide, x_scale, x_data_scale);\n\n')
        f.write('y_scale = zeros(size(x_scale,1),1);\n')
        f.write('for i = 1:nSV\n')
        f.write('   X = bsxfun(@plus, - x_scale, SV(i,:));\n')
        f.write('   X = sum(X.*X,2);\n')
        f.write('   y_scale = y_scale + svCoeff(i) * exp(-X * gamma);\n')
        f.write('end;\n')
        f.write('y_scale = y_scale - rho;\n')
        f.write('y = y_scale * y_data_scale + y_data_bias;')
        f.close()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
        return False
    except ValueError as e:
        print ("Value error: {0}".format(e))
        return False
    except TypeError as e:
        print ("Type error: {0}".format(e))
        return False
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise
