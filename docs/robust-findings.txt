# Robustness extension results

All cells and windows were fixed before substantive training. This is a follow-up sensitivity analysis, not a novel RL method or independent preregistration of earlier findings.

Eight independent market seeds per scenario; treatment forks and windows are dependent. Intervals are paired whole-market percentile bootstrap intervals, not proof of convergence or family-wise significance.

## Primary adaptive protected results, full20k

|Scenario|Arm|CS mean [95% interval]|Profit A|Profit B|Retention|Feasible count|Singleton fraction|Conditional entropy|
|---|---|---:|---:|---:|---:|---:|---:|---:|
|base-g15-t1|none|44.858 [41.507, 47.901]|31.096|31.997|100.00%|15.000|0.00%|0.443|
|base-g15-t1|cap-proposal|72.122 [72.122, 72.122]|22.019|22.019|5.05%|2.000|0.00%|0.009|
|base-g15-t1|guard-proposal|72.119 [72.119, 72.119]|22.020|22.020|0.07%|1.000|100.00%|0.000|
|base-g15-t1|guard-aware|72.119 [72.119, 72.119]|22.020|22.020|100.00%|1.000|100.00%|0.000|
|scale0.5-g15-t1|none|54.961 [51.754, 58.429]|33.251|32.544|100.00%|15.000|0.00%|1.110|
|scale0.5-g15-t1|cap-proposal|69.567 [69.567, 69.567]|29.821|29.821|7.99%|2.000|0.00%|0.009|
|scale0.5-g15-t1|guard-proposal|64.678 [64.675, 64.682]|31.208|31.209|5.47%|3.998|0.00%|0.053|
|scale0.5-g15-t1|guard-aware|64.748 [64.741, 64.757]|31.189|31.188|100.00%|3.993|0.00%|0.154|
|lower-quality-g15-t1|none|27.481 [25.877, 29.214]|16.626|16.272|100.00%|15.000|0.00%|1.110|
|lower-quality-g15-t1|cap-proposal|34.784 [34.783, 34.784]|14.911|14.911|7.99%|2.000|0.00%|0.009|
|lower-quality-g15-t1|guard-proposal|32.339 [32.337, 32.341]|15.604|15.604|5.47%|3.998|0.00%|0.053|
|lower-quality-g15-t1|guard-aware|32.374 [32.370, 32.379]|15.595|15.594|100.00%|3.993|0.00%|0.154|
|lowcost-g15-t1|none|65.309 [60.420, 69.760]|42.833|42.159|100.00%|15.000|0.00%|0.448|
|lowcost-g15-t1|cap-proposal|109.353 [109.352, 109.354]|23.842|23.842|5.17%|2.000|0.00%|0.009|
|lowcost-g15-t1|guard-proposal|109.348 [109.348, 109.348]|23.844|23.844|0.07%|1.000|100.00%|0.000|
|lowcost-g15-t1|guard-aware|109.348 [109.348, 109.348]|23.844|23.844|100.00%|1.000|100.00%|0.000|
|base-g11-t1|none|49.893 [46.845, 52.964]|31.108|29.622|100.00%|11.000|0.00%|0.284|
|base-g11-t1|cap-proposal|70.664 [70.663, 70.664]|22.668|22.669|12.10%|2.000|0.00%|0.011|
|base-g11-t1|guard-proposal|70.658 [70.658, 70.658]|22.671|22.671|0.09%|1.000|100.00%|0.000|
|base-g11-t1|guard-aware|70.658 [70.658, 70.658]|22.671|22.671|100.00%|1.000|100.00%|0.000|
|base-g31-t1|none|49.369 [46.498, 52.290]|30.089|30.125|100.00%|31.000|0.00%|1.297|
|base-g31-t1|cap-proposal|72.365 [72.365, 72.365]|21.910|21.910|2.89%|3.000|0.00%|0.009|
|base-g31-t1|guard-proposal|68.968 [68.967, 68.970]|23.414|23.415|4.51%|3.002|0.00%|0.025|
|base-g31-t1|guard-aware|69.004 [68.998, 69.014]|23.397|23.399|100.00%|3.018|0.00%|0.118|
|base-g15-t0.5|none|44.858 [41.507, 47.901]|31.096|31.997|100.00%|15.000|0.00%|0.443|
|base-g15-t0.5|cap-proposal|72.122 [72.122, 72.122]|22.019|22.019|5.05%|2.000|0.00%|0.009|
|base-g15-t0.5|guard-proposal|72.119 [72.119, 72.119]|22.020|22.020|0.07%|1.000|100.00%|0.000|
|base-g15-t0.5|guard-aware|72.119 [72.119, 72.119]|22.020|22.020|100.00%|1.000|100.00%|0.000|
|base-g15-t2|none|44.858 [41.507, 47.901]|31.096|31.997|100.00%|15.000|0.00%|0.443|
|base-g15-t2|cap-proposal|72.122 [72.122, 72.122]|22.019|22.019|5.05%|2.000|0.00%|0.009|
|base-g15-t2|guard-proposal|68.488 [68.485, 68.491]|23.623|23.624|7.09%|2.003|0.00%|0.026|
|base-g15-t2|guard-aware|68.527 [68.518, 68.536]|23.607|23.605|100.00%|2.013|0.00%|0.088|

## Paired primary contrasts

|Scenario|Contrast|CS difference [95% interval]|CS difference / Nash-to-joint CS gap|Profit A difference|Retention difference|
|---|---|---:|---:|---:|---:|
|base-g15-t1|guard-proposal minus none|27.261 [24.214, 30.612]|0.7026|-9.076|-0.9993|
|base-g15-t1|guard-aware minus guard-proposal|0.000 [0.000, 0.000]|0.0000|0.000|0.9993|
|base-g15-t1|guard-aware minus cap-proposal|-0.003 [-0.003, -0.002]|-0.0001|0.001|0.9495|
|scale0.5-g15-t1|guard-proposal minus none|9.717 [6.248, 12.916]|0.3751|-2.043|-0.9453|
|scale0.5-g15-t1|guard-aware minus guard-proposal|0.070 [0.061, 0.081]|0.0027|-0.019|0.9453|
|scale0.5-g15-t1|guard-aware minus cap-proposal|-4.819 [-4.826, -4.810]|-0.1860|1.368|0.9201|
|lower-quality-g15-t1|guard-proposal minus none|4.858 [3.124, 6.458]|0.3751|-1.021|-0.9453|
|lower-quality-g15-t1|guard-aware minus guard-proposal|0.035 [0.030, 0.040]|0.0027|-0.010|0.9453|
|lower-quality-g15-t1|guard-aware minus cap-proposal|-2.410 [-2.413, -2.405]|-0.1860|0.684|0.9201|
|lowcost-g15-t1|guard-proposal minus none|44.040 [39.587, 48.923]|0.6434|-18.988|-0.9993|
|lowcost-g15-t1|guard-aware minus guard-proposal|0.000 [0.000, 0.000]|0.0000|0.000|0.9993|
|lowcost-g15-t1|guard-aware minus cap-proposal|-0.005 [-0.005, -0.004]|-0.0001|0.003|0.9483|
|base-g11-t1|guard-proposal minus none|20.766 [17.694, 23.813]|0.5352|-8.437|-0.9991|
|base-g11-t1|guard-aware minus guard-proposal|0.000 [0.000, 0.000]|0.0000|0.000|0.9991|
|base-g11-t1|guard-aware minus cap-proposal|-0.005 [-0.006, -0.005]|-0.0001|0.003|0.8790|
|base-g31-t1|guard-proposal minus none|19.599 [16.676, 22.471]|0.5051|-6.674|-0.9549|
|base-g31-t1|guard-aware minus guard-proposal|0.037 [0.031, 0.045]|0.0009|-0.017|0.9549|
|base-g31-t1|guard-aware minus cap-proposal|-3.360 [-3.367, -3.351]|-0.0866|1.487|0.9711|
|base-g15-t0.5|guard-proposal minus none|27.261 [24.214, 30.612]|0.7026|-9.076|-0.9993|
|base-g15-t0.5|guard-aware minus guard-proposal|0.000 [0.000, 0.000]|0.0000|0.000|0.9993|
|base-g15-t0.5|guard-aware minus cap-proposal|-0.003 [-0.003, -0.002]|-0.0001|0.001|0.9495|
|base-g15-t2|guard-proposal minus none|23.629 [20.583, 26.983]|0.6090|-7.474|-0.9291|
|base-g15-t2|guard-aware minus guard-proposal|0.039 [0.031, 0.048]|0.0010|-0.016|0.9291|
|base-g15-t2|guard-aware minus cap-proposal|-3.595 [-3.604, -3.586]|-0.0926|1.588|0.9495|

The complete machine-readable analysis includes every scenario, arm, release condition, learning/exploration fork, full20k and final5k window, and per-seed result. Raw CS levels are not pooled across economies. Entropy is descriptive, and action freedom is not equivalent to retention. No scenario was dropped or extended based on outcomes.
