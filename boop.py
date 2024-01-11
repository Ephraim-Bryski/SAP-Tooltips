def hi(a=None,b=None,c=None):
    all_args = [a,b,c]
    if None in all_args:
        none_idx = all_args.index(None)
        filled_args = all_args[:none_idx]
    else:
        filled_args = all_args
    print(filled_args)

hi()
hi(10)
hi(10,12)
hi(3,4,5,7)