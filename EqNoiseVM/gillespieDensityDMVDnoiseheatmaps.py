import os

import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as M

plt.rcParams["figure.figsize"] = (25, 18)

# colours for the lines and points///add more if needed
colours = ["#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", '#21918c', '#e41a1c']
colours = ["#000000","#3DB7E9", "#F748A5", "#359B73","#e69f00","#2271B2","#f0e442","#d55e00"]

# symbols to be used for gillespie points///add more if needed
symbols = ["o", "v", "*", "d", "h", "X", "P", "+", "^"]

# ======GILLESPIE OR NOT=======#
gillespie_plot = "false"
# =============================#
# ======GILLESPIE OR NOT=======#
equation_plot = "true"
# ==If plotting heatmaps set to true otherwise false will generate SPD==#
heatmaps = "false"
# ==If plotting heatmaps set to true and want bifurcation lines==#
withBif = False
# =============================#

# =========DIRECTORIES FOR bifurcation data -if withBif set to true=========#
opdir_bifurcation = '/Users/rzakir/Documents/fromasus/2022/Eq10MobiliaPRE/bifurcationlines/VM1/'  # os.gtcwd()

# ============================================================#

# array to store gillespie files
data_files = []
# axis range
plt.xlim(-1, 1)
plt.ylim(0, 0.06)
# array to store gillespie points
op1 = []
op2 = []
# array to store formatted gillespie points to be plotted
pointxaxis = []
pointyaxis = []

# to store legend data
patch = []

##=== total number of agents, specify mor ein list if needed===#
#N = [50,100,150,200,250,300,350,400]    # uncomment for varying noise and fixed swarm size and SPD
N=[200]
#N = [50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400]
#================================#
# specify the exponent for q voter model---> fixed to one
q = 1
raa=100
#=== Specify the noise values to plot equation====#
noiselist = [0.001,0.05,0.1,0.2]  # uncomment for SPD
#noiselist = [0.005] #uncomment for varying swarm size
#noiselist = [0.001, 0.0015, 0.002, 0.0025, 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.0065, 0.007, 0.0075, 0.008, 0.0085, 0.009, 0.0095, 0.01, 0.0105, 0.011, 0.0115, 0.012, 0.0125, 0.013, 0.0135, 0.014, 0.0145, 0.015, 0.0155, 0.016, 0.0165, 0.017, 0.0175, 0.018, 0.0185, 0.019, 0.0195, 0.02, 0.0205, 0.021, 0.0215, 0.022, 0.0225, 0.023, 0.0235, 0.024, 0.0245, 0.025, 0.0255, 0.026, 0.0265, 0.027, 0.0275, 0.028, 0.0285, 0.029, 0.0295, 0.03, 0.0305, 0.031, 0.0315, 0.032, 0.0325, 0.033, 0.0335, 0.034, 0.0345, 0.035, 0.0355, 0.036, 0.0365, 0.037, 0.0375, 0.038, 0.0385, 0.039, 0.0395, 0.04, 0.0405, 0.041, 0.0415, 0.042, 0.0425, 0.043, 0.0435, 0.044, 0.0445, 0.045, 0.0455, 0.046, 0.0465, 0.047, 0.0475, 0.048, 0.0485, 0.049, 0.0495, 0.05, 0.0505, 0.051, 0.0515, 0.052, 0.0525, 0.053, 0.0535, 0.054, 0.0545, 0.055, 0.0555, 0.056, 0.0565, 0.057, 0.0575, 0.058, 0.0585, 0.059, 0.0595, 0.06, 0.0605, 0.061, 0.0615, 0.062, 0.0625, 0.063, 0.0635, 0.064, 0.0645, 0.065, 0.0655, 0.066, 0.0665, 0.067, 0.0675, 0.068, 0.0685, 0.069, 0.0695, 0.07, 0.0705, 0.071, 0.0715, 0.072, 0.0725, 0.073, 0.0735, 0.074, 0.0745, 0.075, 0.0755, 0.076, 0.0765, 0.077, 0.0775, 0.078, 0.0785, 0.079, 0.0795, 0.08, 0.0805, 0.081, 0.0815, 0.082, 0.0825, 0.083, 0.0835, 0.084, 0.0845, 0.085, 0.0855, 0.086, 0.0865, 0.087, 0.0875, 0.088, 0.0885, 0.089, 0.0895, 0.09, 0.0905, 0.091, 0.0915, 0.092, 0.0925, 0.093, 0.0935, 0.094, 0.0945, 0.095, 0.0955, 0.096, 0.0965, 0.097, 0.0975, 0.098, 0.0985, 0.099, 0.0995, 0.1, 0.1005, 0.101, 0.1015, 0.102, 0.1025, 0.103, 0.1035, 0.104, 0.1045, 0.105, 0.1055, 0.106, 0.1065, 0.107, 0.1075, 0.108, 0.1085, 0.109, 0.1095, 0.11, 0.1105, 0.111, 0.1115, 0.112, 0.1125, 0.113, 0.1135, 0.114, 0.1145, 0.115, 0.1155, 0.116, 0.1165, 0.117, 0.1175, 0.118, 0.1185, 0.119, 0.1195, 0.12, 0.1205, 0.121, 0.1215, 0.122, 0.1225, 0.123, 0.1235, 0.124, 0.1245, 0.125, 0.1255, 0.126, 0.1265, 0.127, 0.1275, 0.128, 0.1285, 0.129, 0.1295, 0.13, 0.1305, 0.131, 0.1315, 0.132, 0.1325, 0.133, 0.1335, 0.134, 0.1345, 0.135, 0.1355, 0.136, 0.1365, 0.137, 0.1375, 0.138, 0.1385, 0.139, 0.1395, 0.14, 0.1405, 0.141, 0.1415, 0.142, 0.1425, 0.143, 0.1435, 0.144, 0.1445, 0.145, 0.1455, 0.146, 0.1465, 0.147, 0.1475, 0.148, 0.1485, 0.149, 0.1495, 0.15, 0.1505, 0.151, 0.1515, 0.152, 0.1525, 0.153, 0.1535, 0.154, 0.1545, 0.155, 0.1555, 0.156, 0.1565, 0.157, 0.1575, 0.158, 0.1585, 0.159, 0.1595, 0.16, 0.1605, 0.161, 0.1615, 0.162, 0.1625, 0.163, 0.1635, 0.164, 0.1645, 0.165, 0.1655, 0.166, 0.1665, 0.167, 0.1675, 0.168, 0.1685, 0.169, 0.1695, 0.17, 0.1705, 0.171, 0.1715, 0.172, 0.1725, 0.173, 0.1735, 0.174, 0.1745, 0.175, 0.1755, 0.176, 0.1765, 0.177, 0.1775, 0.178, 0.1785, 0.179, 0.1795, 0.18, 0.1805, 0.181, 0.1815, 0.182, 0.1825, 0.183, 0.1835, 0.184, 0.1845, 0.185, 0.1855, 0.186, 0.1865, 0.187, 0.1875, 0.188, 0.1885, 0.189, 0.1895, 0.19, 0.1905, 0.191, 0.1915, 0.192, 0.1925, 0.193, 0.1935, 0.194, 0.1945, 0.195, 0.1955, 0.196, 0.1965, 0.197, 0.1975, 0.198, 0.1985, 0.199, 0.1995, 0.2, 0.2005, 0.201, 0.2015, 0.202, 0.2025, 0.203, 0.2035, 0.204, 0.2045, 0.205, 0.2055, 0.206, 0.2065, 0.207, 0.2075, 0.208, 0.2085, 0.209, 0.2095, 0.21, 0.2105, 0.211, 0.2115, 0.212, 0.2125, 0.213, 0.2135, 0.214, 0.2145, 0.215, 0.2155, 0.216, 0.2165, 0.217, 0.2175, 0.218, 0.2185, 0.219, 0.2195, 0.22, 0.2205, 0.221, 0.2215, 0.222, 0.2225, 0.223, 0.2235, 0.224, 0.2245, 0.225, 0.2255, 0.226, 0.2265, 0.227, 0.2275, 0.228, 0.2285, 0.229, 0.2295, 0.23, 0.2305, 0.231, 0.2315, 0.232, 0.2325, 0.233, 0.2335, 0.234, 0.2345, 0.235, 0.2355, 0.236, 0.2365, 0.237, 0.2375, 0.238, 0.2385, 0.239, 0.2395, 0.24, 0.2405, 0.241, 0.2415, 0.242, 0.2425, 0.243, 0.2435, 0.244, 0.2445, 0.245, 0.2455, 0.246, 0.2465, 0.247, 0.2475, 0.248, 0.2485, 0.249, 0.2495, 0.25, 0.2505, 0.251, 0.2515, 0.252, 0.2525, 0.253, 0.2535, 0.254, 0.2545, 0.255, 0.2555, 0.256, 0.2565, 0.257, 0.2575, 0.258, 0.2585, 0.259, 0.2595, 0.26, 0.2605, 0.261, 0.2615, 0.262, 0.2625, 0.263, 0.2635, 0.264, 0.2645, 0.265, 0.2655, 0.266, 0.2665, 0.267, 0.2675, 0.268, 0.2685, 0.269, 0.2695, 0.27, 0.2705, 0.271, 0.2715, 0.272, 0.2725, 0.273, 0.2735, 0.274, 0.2745, 0.275, 0.2755, 0.276, 0.2765, 0.277, 0.2775, 0.278, 0.2785, 0.279, 0.2795, 0.28, 0.2805, 0.281, 0.2815, 0.282, 0.2825, 0.283, 0.2835, 0.284, 0.2845, 0.285, 0.2855, 0.286, 0.2865, 0.287, 0.2875, 0.288, 0.2885, 0.289, 0.2895, 0.29, 0.2905, 0.291, 0.2915, 0.292, 0.2925, 0.293, 0.2935, 0.294, 0.2945, 0.295, 0.2955, 0.296, 0.2965, 0.297, 0.2975, 0.298, 0.2985, 0.299, 0.2995, 0.3, 0.3005, 0.301, 0.3015, 0.302, 0.3025, 0.303, 0.3035, 0.304, 0.3045, 0.305, 0.3055, 0.306, 0.3065, 0.307, 0.3075, 0.308, 0.3085, 0.309, 0.3095, 0.31, 0.3105, 0.311, 0.3115, 0.312, 0.3125, 0.313, 0.3135, 0.314, 0.3145, 0.315, 0.3155, 0.316, 0.3165, 0.317, 0.3175, 0.318, 0.3185, 0.319, 0.3195, 0.32, 0.3205, 0.321, 0.3215, 0.322, 0.3225, 0.323, 0.3235, 0.324, 0.3245, 0.325, 0.3255, 0.326, 0.3265, 0.327, 0.3275, 0.328, 0.3285, 0.329, 0.3295, 0.33, 0.3305, 0.331, 0.3315, 0.332, 0.3325, 0.333, 0.3335, 0.334, 0.3345, 0.335, 0.3355, 0.336, 0.3365, 0.337, 0.3375, 0.338, 0.3385, 0.339, 0.3395, 0.34, 0.3405, 0.341, 0.3415, 0.342, 0.3425, 0.343, 0.3435, 0.344, 0.3445, 0.345, 0.3455, 0.346, 0.3465, 0.347, 0.3475, 0.348, 0.3485, 0.349, 0.3495, 0.35, 0.3505, 0.351, 0.3515, 0.352, 0.3525, 0.353, 0.3535, 0.354, 0.3545, 0.355, 0.3555, 0.356, 0.3565, 0.357, 0.3575, 0.358, 0.3585, 0.359, 0.3595, 0.36, 0.3605, 0.361, 0.3615, 0.362, 0.3625, 0.363, 0.3635, 0.364, 0.3645, 0.365, 0.3655, 0.366, 0.3665, 0.367, 0.3675, 0.368, 0.3685, 0.369, 0.3695, 0.37, 0.3705, 0.371, 0.3715, 0.372, 0.3725, 0.373, 0.3735, 0.374, 0.3745, 0.375, 0.3755, 0.376, 0.3765, 0.377, 0.3775, 0.378, 0.3785, 0.379, 0.3795, 0.38, 0.3805, 0.381, 0.3815, 0.382, 0.3825, 0.383, 0.3835, 0.384, 0.3845, 0.385, 0.3855, 0.386, 0.3865, 0.387, 0.3875, 0.388, 0.3885, 0.389, 0.3895, 0.39, 0.3905, 0.391, 0.3915, 0.392, 0.3925, 0.393, 0.3935, 0.394, 0.3945, 0.395, 0.3955, 0.396, 0.3965, 0.397, 0.3975, 0.398, 0.3985, 0.399, 0.3995, 0.4, 0.4005, 0.401, 0.4015, 0.402, 0.4025, 0.403, 0.4035, 0.404, 0.4045, 0.405, 0.4055, 0.406, 0.4065, 0.407, 0.4075, 0.408, 0.4085, 0.409, 0.4095, 0.41, 0.4105, 0.411, 0.4115, 0.412, 0.4125, 0.413, 0.4135, 0.414, 0.4145, 0.415, 0.4155, 0.416, 0.4165, 0.417, 0.4175, 0.418, 0.4185, 0.419, 0.4195, 0.42, 0.4205, 0.421, 0.4215, 0.422, 0.4225, 0.423, 0.4235, 0.424, 0.4245, 0.425, 0.4255, 0.426, 0.4265, 0.427, 0.4275, 0.428, 0.4285, 0.429, 0.4295, 0.43, 0.4305, 0.431, 0.4315, 0.432, 0.4325, 0.433, 0.4335, 0.434, 0.4345, 0.435, 0.4355, 0.436, 0.4365, 0.437, 0.4375, 0.438, 0.4385, 0.439, 0.4395, 0.44, 0.4405, 0.441, 0.4415, 0.442, 0.4425, 0.443, 0.4435, 0.444, 0.4445, 0.445, 0.4455, 0.446, 0.4465, 0.447, 0.4475, 0.448, 0.4485, 0.449, 0.4495, 0.45, 0.4505, 0.451, 0.4515, 0.452, 0.4525, 0.453, 0.4535, 0.454, 0.4545, 0.455, 0.4555, 0.456, 0.4565, 0.457, 0.4575, 0.458, 0.4585, 0.459, 0.4595, 0.46, 0.4605, 0.461, 0.4615, 0.462, 0.4625, 0.463, 0.4635, 0.464, 0.4645, 0.465, 0.4655, 0.466, 0.4665, 0.467, 0.4675, 0.468, 0.4685, 0.469, 0.4695, 0.47, 0.4705, 0.471, 0.4715, 0.472, 0.4725, 0.473, 0.4735, 0.474, 0.4745, 0.475, 0.4755, 0.476, 0.4765, 0.477, 0.4775, 0.478, 0.4785, 0.479, 0.4795, 0.48, 0.4805, 0.481, 0.4815, 0.482, 0.4825, 0.483, 0.4835, 0.484, 0.4845, 0.485, 0.4855, 0.486, 0.4865, 0.487, 0.4875, 0.488, 0.4885, 0.489, 0.4895, 0.49, 0.4905, 0.491, 0.4915, 0.492, 0.4925, 0.493, 0.4935, 0.494, 0.4945, 0.495, 0.4955, 0.496, 0.4965, 0.497, 0.4975, 0.498, 0.4985, 0.499, 0.4995, 0.5]
"""
noiselist = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06, 0.065, 0.07, 0.075, 0.08,
             0.085, 0.09, 0.095, 0.1, 0.105, 0.11, 0.115, 0.12, 0.125, 0.13, 0.135, 0.14, 0.145, 0.15, 0.155, 0.16,
             0.165, 0.17, 0.175, 0.18, 0.185, 0.19, 0.195, 0.2, 0.205, 0.21, 0.215, 0.22, 0.225, 0.23, 0.235, 0.24,
             0.245, 0.25, 0.255, 0.26, 0.265, 0.27, 0.275, 0.28, 0.285, 0.29, 0.295, 0.3, 0.305, 0.31, 0.315, 0.32,
             0.325, 0.33, 0.335, 0.34, 0.345, 0.35, 0.355, 0.36, 0.365, 0.37, 0.375, 0.38, 0.385, 0.39, 0.395, 0.4,
             0.405, 0.41, 0.415, 0.42, 0.425, 0.43, 0.435, 0.44, 0.445, 0.45, 0.455, 0.46, 0.465, 0.47, 0.475, 0.48,
             0.485, 0.49, 0.495]
"""
#===============================================#
# specify the qratios, ra is changed to vary qratio for agents A and Za
ra = 1
rb = 1

# =========DIRECTORIES FOR GILLESPIE RUNS-if gillespie_plot set to true=========#
# opdir = 'D:/Simpaperresults/probabilitydistfromGillespieCDCI/datafiles/' # os.getcwd()
opdir = '/Users/rzakir/Documents/fromasus/RunsNoiseVaryZ2/'
# ===============================#

# array to load bifur cation files
data_files_bif = []

# to store bifurcation points to plot
bix = []
biy = []

# ==========FUNCTIONS===================#

# Function "T plus a" for the increase of 1 a
def Tpa(N, a, qa, n):
    return (((N - a) * ((qa * a) + ((n * N) - n))) / (N - 1))


# Function "T minus a" for the decrease of 1 a
def Tma(N, a, qb, n):
    return ((a*(qb*(N-a)+((n*N)-n)))/(N-1))


# ===============================

# to store heatmap data
dump_list_x_points = []
dump_list_y_points = []

if gillespie_plot == "true":
    # get all the gillespie files and store in this array
    data_files += [file for file in sorted(os.listdir(opdir))]
    sorted(data_files)
    print(data_files)

    xx = 0
    for file1 in sorted(data_files):
        if (file1.endswith('.txt')):
            # print(float(file1[23:29]))
            #  Z = 0
            #  S = 200
            # print("The S is: ", S)
            # toadd=int(file1[40:42])*0
            with open(opdir + file1) as f:
                for line in f:
                    # print(line)
                    line.strip()  # Removes \n and spaces on the end
                    # print(line.split()[6])
                    if (line.split()[0] != 'SEED:' and line.split()[0] != 'TS'):
                        # mysum += float(line.split()[2])
                        op1.append(int(float(line.split()[6])))
                        Ntot = int(float(line.split()[6])) + int(float(line.split()[7]))
                print("Length od Op1:", len(op1))
                for i in range(min(op1), max(op1)):
                    # print(float(i / 200))
                    percen = op1.count(i)
                    # print(percen)
                    if (percen != 0):
                        # print(int(i)/int(200))
                        pointxaxis.append((i - (Ntot - i)) / Ntot)
                        pointyaxis.append((percen / len(op1)) * 1)
                        # print(pointyaxis)
                plt.plot(pointxaxis, pointyaxis, symbols[xx], markersize=15, alpha=.8, color=colours[xx])
                if equation_plot != "true":
                    patch.append(mlines.Line2D([], [], color=colours[xx], marker=symbols[xx], markersize=15,
                                               label=str((noiselist[xx]))))

                xx = xx + 1
                # reset variables for next file
                pointxaxis = []
                pointyaxis = []
                op1 = []
                op2 = []


if equation_plot == "true":

    # =========CALCULATE Po=====
    for num, Nval in enumerate(N):

        for Snum in range(0, len(noiselist)):
            print("Snum: ", Snum)
            total_sum = 0
            for k in range(1, Nval + 1):
                #print("Qwfw")
                total_mult = float(1)
                for j in range(0, k):
                    total_mult = total_mult * ((Tpa(Nval,j,ra,noiselist[Snum]))/(Tma(Nval,j+1,rb,noiselist[Snum])))

                    #total_mult = total_mult * (((N - j) / (j + 1)) * ((j + (noiselist[Snum] * N) - noiselist[Snum]) / (-j + ((N - 1) * (1 + noiselist[Snum])))))

                total_sum = total_sum + total_mult
            # disp(total_mult);
            Po1 = 1 / (1 + total_sum)
            print(Po1)
            # ============================
            # =======FIND SPD=============
            plotmexaxis = []
            plotmeyaxis = []
            for plotting in range(0, Nval):
                hans = 1
                for i in range(0, plotting):
                    hans = hans * ((Tpa(Nval,i,ra,noiselist[Snum]))/(Tma(Nval,i+1,rb,noiselist[Snum])))
                   # hans = hans * (((N - i) / (i + 1)) * (
                   #         (i + (noiselist[Snum] * N) - noiselist[Snum]) / (-i + ((N - 1) * (1 + noiselist[Snum])))))
                    # hans = hans * (((N-i)/(i+1))*((j+(noiselist[Snum]*N)-noiselist[Snum])/((-i+(N-1)*(1+noiselist[Snum])))))

                #add SPD points to list for x axis and y axis
                plotmexaxis.append(((plotting - (Nval - (plotting))) / Nval))
                plotmeyaxis.append(Po1 * hans)

                ## get heatmap data to plot if heatmaps=true
                if heatmaps == "true":
                    for i in range(int(Po1 * hans * 155000)):
                        #print(len(N))
                        if len(N) > 1: #when you want varying swarm size and noise fixed (noiselist len=1)
                            dump_list_x_points.append(Nval)
                        elif len(noiselist) > 1: # when you want varying noise and swarm size N is fixed (N len is 1)
                            dump_list_x_points.append(noiselist[Snum])
                        else:
                            print("error, either specify noiselist for heatmaps with fixed N or specify list for N with fixed noise")
                        dump_list_y_points.append(((plotting - (Nval - (plotting))) / Nval))

                # plot SPD only when heatmaps are not to be generated
                if heatmaps == "false":
                    plt.plot(plotmexaxis, plotmeyaxis, linewidth=17, color=colours[Snum])
                    # plt.plot((plotting + (Zplus[Snum]) - (200 - (plotting + (Zplus[Snum])))) / 200, Po1 * hans,'o', color=colours[Snum])

            # just to fix legend according to teh type of plot
            if gillespie_plot == "true":
                patch.append(mlines.Line2D([], [], linewidth=6, color=colours[Snum], marker=symbols[Snum], markersize=15,
                                       label=str((noiselist[Snum]))))
            if heatmaps == "false":
                patch.append(mlines.Line2D([], [], linewidth=17, color=colours[Snum], label=str((noiselist[Snum]))))
# print(dump_list_x_points)
# print(dump_list_y_points)


# plotting heatmaps of heatmaps generation is set to true
if heatmaps == "true":
    plt.hist2d(dump_list_x_points, dump_list_y_points, bins=[32, 30], cmap='Reds', norm=M.colors.LogNorm())
if withBif:
    data_files_bif += [file1 for file1 in os.listdir(opdir_bifurcation)]  # for adding your i
    name1 = sorted(data_files_bif, reverse=True)
    print(data_files_bif)
    for file1 in data_files_bif:
        print(file1)
        with open(opdir_bifurcation + file1, 'r') as f1:
            if (file1.endswith('.txt')):
                if (file1.endswith('P3.txt')):
                    for line1 in f1:
                        bix.append(float(line1.split()[0]) * 100)
                        biy.append((-1 * (100 * float(line1.split()[1])) + 100))
                        ###without formatting:
                        ###bix.append(float(line1.split()[0]))
                        ###bix.append(float(line1.split()[1]))
                        plt.plot(bix, biy, linewidth=14, linestyle='dashed', color="royalblue")
                        # plt.axhline(y=200,linewidth=14, linestyle='dashed', color="royalblue",zorder=1)
                       ## plt.plot(bix,biy,linewidth=14, color=[0.0, 01.0, 0.0])  if qr 1 cdci


                else:
                    if raa == 1:
                        # """
                        point1 = [0, -1]
                        point2 = [0.005, -0.009]
                        x_values = [point1[0], point2[0]]
                        y_values = [point1[1], point2[1]]
                        plt.plot(x_values, y_values, linewidth=14, color=[0.0, 01.0, 0.0])

                        point1 = [0.005, -0.009]
                        point2 = [0.012, 0.00]

                        x_values = [point1[0], point2[0]]
                        y_values = [point1[1], point2[1]]

                        plt.plot(x_values, y_values, linewidth=14, color=[0.0, 01.0, 0.0])

                        point1 = [0.012, 0.00]
                        point2 = [0.5, 0.00]

                        x_values = [point1[0], point2[0]]
                        y_values = [point1[1], point2[1]]

                        plt.plot(x_values, y_values, linewidth=14, color=[0.0, 01.0, 0.0])

                        point1 = [0, 1]
                        point2 = [0.005, 0.009]

                        x_values = [point1[0], point2[0]]
                        y_values = [point1[1], point2[1]]

                        plt.plot(x_values, y_values, linewidth=14, color=[0.0, 01.0, 0.0])

                        point1 = [0.005, 0.009]
                        point2 = [0.012, 0.00]

                        x_values = [point1[0], point2[0]]
                        y_values = [point1[1], point2[1]]

                        plt.plot(x_values, y_values, linewidth=14, color=[0.0, 01.0, 0.0])

                    # """
                    elif raa==100:
                        point1 = [0.025, 0.00]
                        point2 = [100, 0.00]
                        x_values = [point1[0], point2[0]]
                        y_values = [point1[1], point2[1]]
                        plt.hlines(y=0, xmin=0, xmax=400, linewidth=14, color=[0.0, 01.0, 0.0])
                        #plt.plot(x_values, y_values, linewidth=14, color=[0.0, 01.0, 0.0])


                    else:
                        for line1 in f1:
                            bix.append(float(line1.split()[0]))
                            biy.append(float(line1.split()[1]))
                            plt.plot(bix, biy, linewidth=14, color=[0.0, 01.0, 0.0])
                bix = []
                biy = []


# ==========Formatting the plot====================#

plt.xticks(fontsize=44)
plt.yticks(fontsize=44)

if heatmaps == "false":
    plt.xlabel(r'population $X-Y$', fontsize=62)
    plt.ylabel(r'stationary probability distribution', fontsize=62)
    # plt.title('Population Evolution: Zealots- QRatio-2.00, DMVD, N=200', fontsize=32)
    #plt.set_frame_on(False)  # make it transparent
    legend1 = plt.legend(loc="upper right",handles=patch, title=r'noise $σ$', fontsize=44)
    legend1.get_frame().set_alpha(0.001)
    plt.setp(legend1.get_title(), fontsize=62)
else:
    #plt.xlabel(r'swarm size $S$', fontsize=62)
    #plt.xlabel(r'noise $σ$', fontsize=62)
    plt.ylabel(r'population $X-Y$', fontsize=60)
    ax = plt.gca()
    # ax.set_xlim([0, 1])
    ax.set_ylim([-1, 1])
    ax.margins(0)

#plt.savefig('images/Heatmaps_Eq_DMVDvaryingSizeN_dmvd.pdf', dpi=300, bbox_inches='tight')
plt.savefig('images/NEWFIG22/nc22_spd_dmvd_2B_n200_22.pdf', dpi=300, bbox_inches='tight')

plt.show()
