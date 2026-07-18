(function (root, factory) {
    const api = factory();
    if (typeof module === 'object' && module.exports) {
        module.exports = api;
    } else {
        root.PulseAggregation = api;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    const ESTIMATED_GAP_MS = 90 * 60 * 1000;
    const DAY_MS = 24 * 60 * 60 * 1000;

    function getBucketStart(ms, interval) {
        const time = new Date(ms);
        if (interval === 'hour') {
            time.setMinutes(0, 0, 0);
        } else if (interval === 'day') {
            time.setHours(0, 0, 0, 0);
        } else if (interval === 'week') {
            time.setDate(time.getDate() - time.getDay());
            time.setHours(0, 0, 0, 0);
        } else if (interval === 'month') {
            time.setDate(1);
            time.setHours(0, 0, 0, 0);
        }
        return time.getTime();
    }

    function getNextBucketStart(bucketStart, interval) {
        const time = new Date(bucketStart);
        if (interval === 'hour') time.setHours(time.getHours() + 1);
        else if (interval === 'day') time.setDate(time.getDate() + 1);
        else if (interval === 'week') time.setDate(time.getDate() + 7);
        else if (interval === 'month') time.setMonth(time.getMonth() + 1);
        return time.getTime();
    }

    function calculateDiffs(rawData) {
        const diffs = [];
        let recoveryFloor = null;

        for (let i = 1; i < rawData.length; i += 1) {
            const current = rawData[i];
            const previous = rawData[i - 1];
            const currentTime = new Date(current.timestamp).getTime();
            const previousTime = new Date(previous.timestamp).getTime();
            const duration = currentTime - previousTime;
            const currentValue = Number(current.total_submissions) || 0;
            const previousValue = Number(previous.total_submissions) || 0;

            if (duration <= 0 || currentValue <= 0 || previousValue <= 0) continue;
            if (recoveryFloor !== null) {
                if (currentValue >= recoveryFloor) recoveryFloor = null;
                continue;
            }
            if (currentValue < previousValue) {
                recoveryFloor = previousValue;
                continue;
            }

            diffs.push({
                startTime: previousTime,
                endTime: currentTime,
                value: currentValue - previousValue,
                duration,
                estimated: duration > ESTIMATED_GAP_MS
            });
        }
        return diffs;
    }

    function aggregateData(rawData, interval) {
        const diffs = calculateDiffs(rawData);
        if (interval === 'raw') {
            return diffs.map(diff => ({
                timestamp: new Date(diff.endTime),
                value: diff.value,
                estimated: diff.estimated
            }));
        }

        const buckets = new Map();
        diffs.forEach(diff => {
            if (diff.value === 0) return;

            let bucketStart = getBucketStart(diff.startTime, interval);
            const lastBucketStart = getBucketStart(diff.endTime - 1, interval);
            const estimatedContribution = diff.estimated && bucketStart !== lastBucketStart;
            const rate = diff.value / diff.duration;
            let cursor = diff.startTime;

            while (cursor < diff.endTime) {
                const bucketEnd = getNextBucketStart(bucketStart, interval);
                const segmentEnd = Math.min(diff.endTime, bucketEnd);
                const overlap = segmentEnd - cursor;
                if (overlap > 0) {
                    const bucket = buckets.get(bucketStart) || { value: 0, estimated: false };
                    bucket.value += overlap * rate;
                    bucket.estimated = bucket.estimated || estimatedContribution;
                    buckets.set(bucketStart, bucket);
                }
                cursor = segmentEnd;
                if (cursor < diff.endTime) bucketStart = bucketEnd;
            }
        });

        return Array.from(buckets.keys())
            .sort((a, b) => a - b)
            .map(key => ({
                timestamp: new Date(key),
                value: Math.round(buckets.get(key).value),
                estimated: buckets.get(key).estimated
            }));
    }

    function chartWindow(data, interval, latestSampleTimestamp) {
        if (data.length === 0) return data;
        const latestSampleTime = new Date(latestSampleTimestamp).getTime();
        const completeData = data.filter(point => (
            getNextBucketStart(point.timestamp.getTime(), interval) <= latestSampleTime
        ));
        if (completeData.length === 0 || interval === 'month') return completeData;

        const latestTime = completeData[completeData.length - 1].timestamp.getTime();
        const windowDays = interval === 'hour' ? 7 : interval === 'day' ? 90 : 365;
        const cutoff = latestTime - windowDays * DAY_MS;
        return completeData.filter(point => point.timestamp.getTime() >= cutoff);
    }

    function formatBucket(timestamp, interval) {
        const start = new Date(timestamp);
        if (interval === 'hour') {
            const end = new Date(getNextBucketStart(start.getTime(), interval));
            const day = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const startTime = start.toLocaleTimeString('en-US', { hour: 'numeric' });
            const endTime = end.toLocaleTimeString('en-US', { hour: 'numeric' });
            return `between ${startTime} and ${endTime} on ${day}`;
        }
        if (interval === 'day') {
            return `on ${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
        }
        if (interval === 'week') {
            const end = new Date(start);
            end.setDate(end.getDate() + 6);
            const from = start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const to = end.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            return `from ${from} to ${to}`;
        }
        return `in ${start.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}`;
    }

    return { aggregateData, chartWindow, formatBucket, getBucketStart, getNextBucketStart };
}));
