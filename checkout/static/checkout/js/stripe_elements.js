var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');

card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

var form = document.getElementById('payment-form');
var submitButton = document.getElementById('submit-button');
var spinner = document.getElementById('spinner');
var lockIcon = document.getElementById('lock-icon');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true });
    submitButton.disabled = true;
    spinner.style.display = 'inline-block';
    lockIcon.style.display = 'none';

    var billingDetails = {
        name: $.trim(form.full_name.value),
        phone: $.trim(form.phone_number.value),
        email: $.trim(form.email.value),
        address:{
            line1: $.trim(form.street_address1.value),
            line2: $.trim(form.street_address2.value),
            city: $.trim(form.town_or_city.value),
            country: $.trim(form.country.value),
            state: $.trim(form.county.value),
        }
    };

    var shippingDetails = {
        name: $.trim(form.full_name.value),
        phone: $.trim(form.phone_number.value),
        address: {
            line1: $.trim(form.street_address1.value),
            line2: $.trim(form.street_address2.value),
            city: $.trim(form.town_or_city.value),
            country: $.trim(form.country.value),
            postal_code: $.trim(form.postcode.value),
            state: $.trim(form.county.value),
        }
    };

    stripe.confirmCardPayment(clientSecret, {
        payment_method: {
            card: card,
            billing_details: billingDetails
        },
        shipping: shippingDetails
    }).then(function(result) {
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            var html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            card.update({ 'disabled': false });
            submitButton.disabled = false;
            spinner.style.display = 'none';
            lockIcon.style.display = 'inline';
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            } else {
                card.update({ 'disabled': false });
                submitButton.disabled = false;
                spinner.style.display = 'none';
                lockIcon.style.display = 'inline';
            }
        }
    });
});
