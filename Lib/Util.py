def bytes_to_human(bytes, metric_list=[[1024**4, 'TiB'], [1024**3, 'GiB'], [1024**2, 'MiB'], [1024, 'KiB'], [1, 'B']]):
    """Returns user-readable representation of given bytes"""
    bytes = int(bytes)

    output = ''
    for metric_count, metric_char in metric_list:
        if bytes >= metric_count:
            bytes = (float(bytes) / metric_count)
            metric_string = '{:.1f}'.format(bytes).replace('.0', '')
            output += '{}{}'.format(metric_string, metric_char)

            return output

    return output
