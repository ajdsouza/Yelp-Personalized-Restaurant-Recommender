import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA as sklearnPCA

if __name__ == '__main__':
    pass

    df = pd.read_csv("file:///Users/paramadutta/yelp/allFeatures.csv")
    
    # Remove the IS_DISH column name
    cols = df.columns.tolist()
    cols.remove('IS_DISH')
    predictors = df[cols]
    sklearn_pca = sklearnPCA(n_components=2)
    sklearn_transf = sklearn_pca.fit_transform(predictors)
    
    print sklearn_transf
    
    
    plt.plot([.801],[0.65],
             'o', markersize=7, color='blue', alpha=0.5)

    plt.plot([1.21],[0.75],
             'o', markersize=7, color='blue', alpha=0.5)

    plt.plot([1.51],[0.65],
             'o', markersize=7, color='blue', alpha=0.5)

    plt.plot([0.85],[0.325],
             'o', markersize=7, color='blue', alpha=0.5)

    plt.plot([0.55],[0.125],
             'o', markersize=7, color='blue', alpha=0.5)
    plt.plot(sklearn_transf[0:2227,0],sklearn_transf[0:2227,1],
             'o', markersize=7, color='blue', alpha=0.5, label='dishname')
    plt.plot(sklearn_transf[2228:9670,0], sklearn_transf[2228:9670,1],
             '^', markersize=7, color='red', alpha=0.5, label='not_dishname')

    
    plt.xlabel('x_values')
    plt.ylabel('y_values')
    plt.xlim([-2,3])
    plt.ylim([-2,2])
    plt.legend()
    plt.title('Transformed samples')
    plt.show()
