from django.shortcuts import render
from .models import Facility, SupplyHub

def coverage_report(request):
    facilities = Facility.objects.all()
    hubs = SupplyHub.objects.filter(active=True)

    facility_data = []
    covered_count = 0

    for f in facilities:
        hub, dist = f.nearest_hub()
        is_covered = f.is_covered()
        if is_covered:
            covered_count += 1

        facility_data.append({
            'facility': f,
            'nearest_hub': hub,
            'distance_km': round(dist, 2) if dist is not None else None,
            'is_covered': is_covered,
        })

    total = facilities.count()
    coverage_percent = round((covered_count / total) * 100, 1) if total > 0 else 0

    context = {
        'facility_data': facility_data,
        'total_facilities': total,
        'covered_count': covered_count,
        'coverage_percent': coverage_percent,
        'hubs': hubs,
    }
    return render(request, 'coverage_report.html', context)