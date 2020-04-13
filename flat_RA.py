# Implementation of the right atrial (RA) flattening described in "Standard quasi-conformal flattening of the right
# and left atria", Nunez-Garcia, Marta, et al., Functional Imaging and Modeling of the Heart. FIMH 2019.
# Lecture Notes in Computer Science, vol 11504

# Input: RA mesh with clipped holes corresponding to tricuspid valve (TV), superior and inferior vena cava.
# Output: Flat (2D) version of the input mesh.
# Usage: python flat_RA.py --meshfile data/RA_clipped_lines_p5000_15.vtk --flip True


# CAREFULL!!! It may be necessary to try if the flip of the contours (TV, SVC and IVC) is necessary or not.
# The orientation is not found automatically as in the case of the LA and this manual check & modification is
# needed to have consistent orientation of all the maps. Representing them in the -z plane should correspond to
# a view "from the outside", where the RAA is placed on the right
# In the FIMH paper, the 3 examples from Fig. 3 required different flip than the mesh in Fig. 2


from aux_functions import *
import argparse
from sys import platform

parser = argparse.ArgumentParser()
parser.add_argument('--meshfile', type=str, metavar='PATH', help='path to input mesh')
parser.add_argument('--flip', type=bool, default=False, help='Specifiy if a flip of the contours is required (try both cases)')
args = parser.parse_args()

m_closed_filename = args.meshfile[0:len(args.meshfile)-4] + '_c.vtk'
seeds_filename = args.meshfile[0:len(args.meshfile)-4] + '_seeds.vtk'
to_be_flat_filename = args.meshfile[0:len(args.meshfile)-4] + '_to_be_flat.vtk'
m_out_filename = args.meshfile[0:len(args.meshfile) - 4] + '_flat.vtk'

# define disk parameters (external radio, size & position holes, and position of the appendage-apex point)
rdisk = 0.5
rhole_ivc = 0.05
xhole_ivc = 0.0
yhole_ivc = -0.25
rhole_svc = 0.05
xhole_svc = 0.0
yhole_svc = 0.0
app_x0 = np.array([0.10])
app_y0 = np.array([0.10])

if not os.path.exists(args.meshfile):
    exit('ERROR: Input file not found')

# Fill holes
if not os.path.exists(m_closed_filename):
    #os.system("./FillSurfaceHoles -i " + args.meshfile + " -o " + m_closed_filename)
    if platform == "linux" or platform == "linux2":
        os.system('./FillSurfaceHoles -i ' + args.meshfile_open + ' -o ' + args.meshfile_closed)
    elif platform == "win32":
        os.system('FillSurfaceHoles_Windows\FillSurfaceHoles.exe -i ' + args.meshfile_open + ' -o ' + args.meshfile_closed + ' -smooth none')   # default smooth cotangent (and edglen) fails when using this binary
    else:
        sys.exit('Unknown operating system. Holes cannot be filled automatically. Fill holes manually and save file as ', m_closed_filename, '. Then run again this script to proyect scalar arrays from initial mesh if necessary.')

# Mark filled holes with scalar array
m_input = readvtk(args.meshfile)
surface = readvtk(m_closed_filename)
surface = mark_filled_holes(m_input, surface)

# Manually select seeds (launch interactive GUI)
select_RA_seeds(surface, seeds_filename)
seeds_poly = readvtk(seeds_filename)

# Find corresponding seeds in the complete mesh
locator = vtk.vtkPointLocator()
locator.SetDataSet(surface)
locator.BuildLocator()
id_app = locator.FindClosestPoint(seeds_poly.GetPoint(0))
id_svc = locator.FindClosestPoint(seeds_poly.GetPoint(1))
id_ivc = locator.FindClosestPoint(seeds_poly.GetPoint(2))

# Remove holes, save mesh as the one that is going to be flattened.
m_open = pointthreshold(surface, "hole", 0, 0)
transfer_all_scalar_arrays(m_input, m_open)
writevtk(m_open, to_be_flat_filename)
# Initialize locator to find point correspondences between the to_be_flat mesh and other meshes
locator_open = vtk.vtkPointLocator()
locator_open.SetDataSet(m_open)
locator_open.BuildLocator()

# Detect and identify the corresponding edges (hole contours)
edges = extractboundaryedge(m_open)
conn = get_connected_edges(edges)
if conn.GetNumberOfExtractedRegions() != 3:
    print('WARNING: the number of contours detected is not the expected. The classification of contours may be wrong')
poly_edges = conn.GetOutput()
# writevtk(poly_edges, args.meshfile[0:len(args.meshfile)-4] + '_detected_edges.vtk'))
[tv_cont, svc_cont, ivc_cont] = identify_RA_contours(poly_edges, seeds_poly)
[tv_cont_ids, svc_cont_ids, ivc_cont_ids] = identify_ordered_RA_contours_in_to_be_flat_mesh(locator_open, tv_cont, svc_cont, ivc_cont)

# Find intersecting points between dividing paths and contours (holes) to reorder contour ids and set the specific position of the contour points in the template
# e.g. intersection between path1 and IVC corresponds to angle = pi/2 in the lowest hole.
cont = extractlargestregion(edges)   # detect contour of the tricuspid valve (largest boundary)
edge_cont_ids = get_ordered_cont_ids_based_on_distance(cont).astype(int)
id_tv0, id_tv1 = find_tv_extremes(cont, seeds_poly, locator)
path0, path1, path2 = create_dividing_paths(surface, id_tv0, id_tv1, id_svc, id_ivc, args)
s0_ids, s1_ids, s2_ids = project_paths_to_open_mesh(m_open, locator_open, path0, path1, path2)

# TV == external disk, reorder ids to start in TV1 (angle = -pi/2, connection with IVC)
reordered_tv_cont = reorder_tv(surface, locator_open, tv_cont_ids, id_tv0, id_tv1, args)
complete_circumf_t = np.linspace(3*np.pi/2, 3*np.pi/2 + 2*np.pi, len(reordered_tv_cont), endpoint=False)  # starting in -pi/2 or 3pi/2
x0_ext = np.cos(complete_circumf_t) * rdisk
y0_ext = np.sin(complete_circumf_t) * rdisk

# IVC
reordered_ivc_cont = reorder_ivc(ivc_cont_ids, s2_ids, args)
complete_circumf_t = np.linspace(3*np.pi/2, 3*np.pi/2 + 2*np.pi, len(reordered_ivc_cont), endpoint=False)
x0_ivc = np.cos(complete_circumf_t) * rhole_ivc + xhole_ivc
y0_ivc = np.sin(complete_circumf_t) * rhole_ivc + yhole_ivc

# SVC
reordered_svc_cont = reorder_svc(svc_cont_ids, s1_ids, args)
complete_circumf_t = np.linspace(3*np.pi/2, 3*np.pi/2 + 2*np.pi, len(reordered_svc_cont), endpoint=False)
x0_svc = np.cos(complete_circumf_t) * rhole_svc + xhole_svc
y0_svc = np.sin(complete_circumf_t) * rhole_svc + yhole_svc

# Append all the point ids and all the (x,y) coordinates for the contours (constrained points)
aux1 = np.append(reordered_tv_cont, reordered_ivc_cont)
all_contours = np.append(aux1, reordered_svc_cont)

aux2 = np.append(x0_ext, x0_ivc)
all_x0 = np.append(aux2, x0_svc)

aux3 = np.append(y0_ext, y0_ivc)
all_y0 = np.append(aux3, y0_svc)

# Add condition for the appendage apex
p_app = np.array([int(locator_open.FindClosestPoint(surface.GetPoint(id_app)))])
print('Appendage-apex point is', p_app[0])

# Flat
m_disk = flat_w_constraints(m_open, all_contours, p_app, all_x0, all_y0, app_x0, app_y0)
# Refine
m_final = flat_w_constraints(m_disk, all_contours, p_app, all_x0, all_y0, app_x0, app_y0)

# Transfer point information and write output mesh
transfer_all_scalar_arrays_by_point_id(m_open, m_final)
m_final.GetPointData().RemoveArray('hole')
writevtk(m_final, m_out_filename)
