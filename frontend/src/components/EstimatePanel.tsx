import {
    useEffect,
    useState,
} from 'react';

import {
    estimateArea,
    type EstimateAssumptions,
    type EstimateResponse,
} from '../api/api';

import type {
    SelectedArea,
} from '../types/area';

type EstimatePanelProps = {
    selectedArea: SelectedArea | null;
};


const DEFAULT_ASSUMPTIONS: EstimateAssumptions = {

    eligible_address_ratio: 0.90,

    seconds_per_delivery: 10,

    service_distance_factor: 1.45,

    walking_speed_kmh: 4.0,

    exception_rate: 0.05,

    seconds_per_exception: 20,

    fixed_setup_minutes: 20,

    labour_rate_per_hour: 30,

    other_costs: 0,

    target_margin: 0.30,
};

const currencyFormatter =
    new Intl.NumberFormat(
        'en-AU',
        {
            style: 'currency',
            currency: 'AUD',
        },
    );

function EstimatePanel({ selectedArea }: EstimatePanelProps) {
    const [
        assumptions,
        setAssumptions,
    ] = useState<EstimateAssumptions>(
        {
            ...DEFAULT_ASSUMPTIONS,
        }
    );

    const [
        result,
        setResult,
    ] = useState<EstimateResponse | null>(
        null
    );

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState<string | null>(
        null
    );

    useEffect(() => {

        setResult(null);
        setError(null);

    }, [selectedArea]);

    function updateAssumption(
        key: keyof EstimateAssumptions,
        value: number,
    ) {

        setAssumptions(
            current => ({
                ...current,
                [key]: value,
            })
        );

        // Existing estimate is now based on
        // old assumptions, so discard it.
        setResult(null);
    }

    async function handleCalculate() {

        if (!selectedArea) {
            return;
        }

        setLoading(true);
        setError(null);

        try {

            const data = await estimateArea(
                selectedArea.geometry,
                assumptions,
            );

            setResult(data);

        } catch (err) {

            console.error(
                'Estimate failed:',
                err,
            );

            setError(
                'Unable to calculate estimate.'
            );

        } finally {

            setLoading(false);
        }
    }

    return (
        <aside className="estimate-panel">

            <h3>Work estimate</h3>

            {!selectedArea && (
                <p>
                    Select a suburb or draw an area
                    to create an estimate.
                </p>
            )}

            {selectedArea && (
                <>
                    <p className="estimate-area-name">
                        {selectedArea.label}
                    </p>
                    <div className="estimate-field">

                        <label
                            htmlFor="eligible-address-ratio"
                        >
                            Eligible addresses (%)
                        </label>

                        <input
                            id="eligible-address-ratio"

                            type="number"

                            min="0"
                            max="100"
                            step="1"

                            value={
                                assumptions
                                    .eligible_address_ratio
                                * 100
                            }

                            onChange={(event) => {

                                updateAssumption(
                                    'eligible_address_ratio',

                                    Number(
                                        event.target.value
                                    ) / 100,
                                );

                            }}
                        />

                    </div>

                    <div className="estimate-field">

                        <label
                            htmlFor="walking-speed"
                        >
                            Service speed (km/h)
                        </label>

                        <input
                            id="walking-speed"

                            type="number"

                            min="0.1"
                            max="10"
                            step="0.1"

                            value={
                                assumptions.walking_speed_kmh
                            }

                            onChange={(event) => {

                                updateAssumption(
                                    'walking_speed_kmh',
                                    Number(
                                        event.target.value
                                    ),
                                );

                            }}
                        />

                    </div>

                    <div className="estimate-field">

                        <label
                            htmlFor="labour-rate"
                        >
                            Labour rate ($/hour)
                        </label>

                        <input
                            id="labour-rate"

                            type="number"

                            min="0"
                            step="1"

                            value={
                                assumptions
                                    .labour_rate_per_hour
                            }

                            onChange={(event) => {

                                updateAssumption(
                                    'labour_rate_per_hour',

                                    Number(
                                        event.target.value
                                    ),
                                );

                            }}
                        />

                    </div>

                    <div className="estimate-field">

                        <label
                            htmlFor="target-margin"
                        >
                            Target margin (%)
                        </label>

                        <input
                            id="target-margin"

                            type="number"

                            min="0"
                            max="99"
                            step="1"

                            value={
                                assumptions.target_margin
                                * 100
                            }

                            onChange={(event) => {

                                updateAssumption(
                                    'target_margin',

                                    Number(
                                        event.target.value
                                    ) / 100,
                                );

                            }}
                        />

                    </div>

                    <details
                        className="advanced-assumptions"
                    >

                        <summary>
                            Advanced assumptions
                        </summary>
                        <div className="estimate-field">

                            <label
                                htmlFor="seconds-delivery"
                            >
                                Seconds per delivery
                            </label>

                            <input
                                id="seconds-delivery"

                                type="number"

                                min="1"
                                step="1"

                                value={
                                    assumptions
                                        .seconds_per_delivery
                                }

                                onChange={(event) => {

                                    updateAssumption(
                                        'seconds_per_delivery',

                                        Number(
                                            event.target.value
                                        ),
                                    );

                                }}
                            />

                        </div>

                        <div className="estimate-field">

                            <label
                                htmlFor="distance-factor"
                            >
                                Service distance factor
                            </label>

                            <input
                                id="distance-factor"

                                type="number"

                                min="1"
                                max="5"
                                step="0.05"

                                value={
                                    assumptions
                                        .service_distance_factor
                                }

                                onChange={(event) => {

                                    updateAssumption(
                                        'service_distance_factor',

                                        Number(
                                            event.target.value
                                        ),
                                    );

                                }}
                            />

                        </div>

                        <div className="estimate-field">

                            <label
                                htmlFor="exception-rate"
                            >
                                Exception rate (%)
                            </label>

                            <input
                                id="exception-rate"

                                type="number"

                                min="0"
                                max="100"
                                step="1"

                                value={
                                    assumptions.exception_rate
                                    * 100
                                }

                                onChange={(event) => {

                                    updateAssumption(
                                        'exception_rate',

                                        Number(
                                            event.target.value
                                        ) / 100,
                                    );

                                }}
                            />

                        </div>

                        <div className="estimate-field">

                            <label
                                htmlFor="seconds-exception"
                            >
                                Seconds per exception
                            </label>

                            <input
                                id="seconds-exception"

                                type="number"

                                min="0"
                                step="1"

                                value={
                                    assumptions
                                        .seconds_per_exception
                                }

                                onChange={(event) => {

                                    updateAssumption(
                                        'seconds_per_exception',

                                        Number(
                                            event.target.value
                                        ),
                                    );

                                }}
                            />

                        </div>

                        <div className="estimate-field">

                            <label
                                htmlFor="setup-minutes"
                            >
                                Fixed setup time (min)
                            </label>

                            <input
                                id="setup-minutes"

                                type="number"

                                min="0"
                                step="5"

                                value={
                                    assumptions
                                        .fixed_setup_minutes
                                }

                                onChange={(event) => {

                                    updateAssumption(
                                        'fixed_setup_minutes',

                                        Number(
                                            event.target.value
                                        ),
                                    );

                                }}
                            />

                        </div>

                        <div className="estimate-field">

                            <label
                                htmlFor="other-costs"
                            >
                                Other costs ($)
                            </label>

                            <input
                                id="other-costs"

                                type="number"

                                min="0"
                                step="1"

                                value={
                                    assumptions.other_costs
                                }

                                onChange={(event) => {

                                    updateAssumption(
                                        'other_costs',

                                        Number(
                                            event.target.value
                                        ),
                                    );

                                }}
                            />

                        </div>
                    </details>
                    <button
                        className="estimate-button"

                        type="button"

                        disabled={loading}

                        onClick={handleCalculate}
                    >

                        {
                            loading
                                ? 'Calculating...'
                                : 'Calculate estimate'
                        }

                    </button>
                    {error && (
                        <p className="estimate-error">
                            {error}
                        </p>
                    )}

                    {result && (

                        <div className="estimate-results">

                            <h4>Estimate</h4>
                            <div className="estimate-result-row">

                                <span>
                                    Eligible delivery points
                                </span>

                                <strong>
                                    {
                                        result
                                            .estimate
                                            .eligible_delivery_points
                                            .toLocaleString()
                                    }
                                </strong>

                            </div>
                            <div className="estimate-result-row">

                                <span>
                                    Service distance
                                </span>

                                <strong>
                                    {
                                        result
                                            .estimate
                                            .estimated_service_distance_km
                                            .toFixed(1)
                                    }
                                    {' km'}
                                </strong>

                            </div>
                            <div className="estimate-result-row">

                                <span>
                                    Estimated labour
                                </span>

                                <strong>
                                    {
                                        result
                                            .estimate
                                            .estimated_hours
                                            .toFixed(1)
                                    }
                                    {' h'}
                                </strong>

                            </div>
                            <div className="estimate-result-row">

                                <span>
                                    Estimated cost
                                </span>

                                <strong>
                                    {
                                        currencyFormatter.format(
                                            result
                                                .estimate
                                                .estimated_cost
                                        )
                                    }
                                </strong>

                            </div>
                            <div
                                className="
                  estimate-result-row
                  estimate-primary-result
                "
                            >

                                <span>
                                    Suggested quote
                                </span>

                                <strong>
                                    {
                                        currencyFormatter.format(
                                            result
                                                .estimate
                                                .suggested_quote
                                        )
                                    }
                                </strong>

                            </div>
                            <div className="estimate-result-row">

                                <span>
                                    Quote / point
                                </span>

                                <strong>
                                    {
                                        result.estimate
                                            .quote_per_point !== null
                                            ? currencyFormatter.format(
                                                result
                                                    .estimate
                                                    .quote_per_point
                                            )
                                            : 'N/A'
                                    }
                                </strong>

                            </div>
                            <div className="estimate-result-row">

                                <span>
                                    Estimated points / hour
                                </span>

                                <strong>
                                    {
                                        result.estimate
                                            .estimated_points_per_hour
                                            !== null

                                            ? result
                                                .estimate
                                                .estimated_points_per_hour
                                                .toFixed(0)

                                            : 'N/A'
                                    }
                                </strong>

                            </div>
                            <details
                                className="estimate-breakdown"
                            >

                                <summary>
                                    Time breakdown
                                </summary>
                                <div className="estimate-result-row">

                                    <span>
                                        Delivery handling
                                    </span>

                                    <span>
                                        {
                                            result
                                                .estimate
                                                .handling_hours
                                                .toFixed(2)
                                        } h
                                    </span>

                                </div>
                                <div className="estimate-result-row">

                                    <span>
                                        Movement
                                    </span>

                                    <span>
                                        {
                                            result
                                                .estimate
                                                .movement_hours
                                                .toFixed(2)
                                        } h
                                    </span>

                                </div>
                                <div className="estimate-result-row">

                                    <span>
                                        Exceptions
                                    </span>

                                    <span>
                                        {
                                            result
                                                .estimate
                                                .exception_hours
                                                .toFixed(2)
                                        } h
                                    </span>

                                </div>
                                <div className="estimate-result-row">

                                    <span>
                                        Fixed setup
                                    </span>

                                    <span>
                                        {
                                            result
                                                .estimate
                                                .setup_hours
                                                .toFixed(2)
                                        } h
                                    </span>

                                </div>
                            </details>
                            <div className="estimate-model-note">

                                <strong>
                                    Provisional model
                                </strong>

                                <p>
                                    Model version:{' '}
                                    {
                                        result
                                            .estimate
                                            .model_version
                                    }
                                </p>

                                <p>
                                    {
                                        result
                                            .estimate
                                            .model_note
                                    }
                                </p>

                            </div>
                        </div>

                    )}

                </>
            )}

        </aside>
    );
}

export default EstimatePanel;