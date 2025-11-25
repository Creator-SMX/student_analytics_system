try:
    import sklearn
    print(f"scikit-learn版本: {sklearn.__version__}")
    from sklearn.cluster import KMeans
    print("成功导入KMeans")
except ImportError as e:
    print(f"导入错误: {e}")