// Include Files
#include "rt_nonfinite.h"
#include "%%funcName%%.h"
#include "sum.h"
#include "bsxfun.h"

// Function Definitions

//
// Automatic code generation by Kevin Koosup Yum
// Arguments    : const double x[7]
// Return Type  : double
//
double %%funcName%%(const double x[%%noInput%%])
{
  static const double dv9[%%noInput%%] = { %%x_data_bias%% };

  double x_scale[%%noInput%%];
  double b_x_scale[%%noInput%%];
  int i3;
  static const double dv10[%%noInput%%] = { %%x_data_scale%% };

  double y_scale;
  int i;
  double SV[%%noInput%%];
  double X[%%noInput%%];
  static const double b_SV[%%nSVElem%%] = { %%SVElem%% };

  static const double dv11[%%nSV%%] = { %%svCoeff%% };

  bsxfun(x, dv9, x_scale);
  for (i3 = 0; i3 < %%noInput%%; i3++) {
    b_x_scale[i3] = x_scale[i3];
  }

  b_bsxfun(b_x_scale, dv10, x_scale);
  y_scale = 0.0;
  for (i = 0; i < %%nSV%%; i++) {
    for (i3 = 0; i3 < %%noInput%%; i3++) {
      b_x_scale[i3] = -x_scale[i3];
      SV[i3] = b_SV[i + %%nSV%% * i3];
    }

    c_bsxfun(b_x_scale, SV, X);
    for (i3 = 0; i3 < %%noInput%%; i3++) {
      b_x_scale[i3] = X[i3] * X[i3];
    }

    y_scale += dv11[i] * exp(-sum(b_x_scale) * %%gamma%%);
  }

  y_scale -= %%rho%%;
  return y_scale * %%y_data_scale%% + %%y_data_bias%%;
}

//
// File trailer for SVM_ISFC0.cpp
//
// [EOF]
//
