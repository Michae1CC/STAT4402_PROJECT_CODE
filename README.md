# STAT4402 PROJECT
Source code and data files for the STAT4402 project

## Code Listing
A brief overview of the purpose of each file within the GitHub repository.


- `candiy\spectrum-master`- Taken from the GitHub repository of the base paper, see: https://github.com/chopralab/candiy_spectrum.

- `src\data\aggregate\data.py`- Collects scrubbed IR, MS and label vectors to create the final shuffled labelled feature vectors with their corresponding labels.

- `src\data\dataread.py`- Bins IR data given a file containing a matrix of IR values.

- `src\data\example\data\load.py`- Gives an example of loading data for testing and training.

- `src\data\extract\mass\spec.py`- Extracts Mass Spec data from a folder contain jdx files with Mass Spec data.

- `src\data\graph\IR.py`- Graphs input IR data.

- `src\data\graph\MS.py`- Graphs input MS data.

- `src\data\jdxread\IR.py`- Extracts IR data from a folder contain jdx files with IR data.

- `src\data\label\func.py`- Creates a label for a given molecule.

- `src\data\MS\dist.py`- Creates the shifted Mass Spec data.

- `src\data\shuffle\final\data.py`- Creates a shuffled version of the final data.

- `src\data\submit\aggregate.sh`- Submits a job to `getafix`to create the aggregate data.

- `src\data\submit\IR.sh`- Submits a job to `getafix`to create the IR data.

- `src\model\autoencoder\and\mlp.py`- Preliminary run of using an auto-encoder for dimensionality reduction along with a MLP.

- `src\model\best\load\train\auto.py`- Usage of the best model that loads an existing dual channel auto-encoder.

- `src\model\best\model.py`- The best model that was produced in the report.

- `src\model\cluster\20\10\load\auto.py`- A script sent to the cluster to perform a grid search over the MLP parameter space.

- `src\model\cluster\auto\params.py`- A script sent to the cluster to perform a grid search over the auto-encoder parameter space.

- `src\model\cnn\project\stat4402.py`- A trial script for using CNN as a classifier.

- `src\model\create\mlp\jobs.py`- Created cluster jobs for grid searches.

- `src\model\early\models.py`- Early models type checks to see feasibility of classification in RF and SVM.

- `src\model\find\opt\auto\params.py`- Find the best results from cluster outputs.

- `src\model\load\auto.py`- Loads a pickled auto-encoder.

- `src\model\mlp\draft\16\10.py`- Initial MLP model used.

- `src\model\MLP\Overfitting\plot.py`- Plots graphs to check for over fitting in model.

- `src\model\pca\alde\best\mlp.py`- Preliminary run of using PCA for dimensionality 
reduction along with a MLP.
- `src\model\train\auto.py`- A script use to train and pickle an auto-encoder.