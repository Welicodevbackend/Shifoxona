(function($) {
    'use strict';

    $(document).ready(function() {
        // Jazzmin/Select2 ishlatilganda id_department-ni kuzatish
        $('#id_department').on('select2:select change', function (e) {
            var deptId = $(this).val();
            var $doctorField = $('#id_doctor');

            console.log("Bo'lim tanlandi, ID:", deptId);

            if (deptId) {
                $.ajax({
                    url: '/get-doctors-by-dept/',
                    data: {'dept_id': deptId},
                    success: function(data) {
                        // Doktor dropdown-ni tozalash
                        $doctorField.empty();
                        $doctorField.append('<option value="">---------</option>');

                        // Yangi doktorlarni qo'shish
                        $.each(data.doctors, function(index, dr) {
                            var option = new Option(dr.full_name, dr.id, false, false);
                            $doctorField.append(option);
                        });

                        // Select2 ko'rinishini majburiy yangilash
                        if ($doctorField.data('select2')) {
                            $doctorField.trigger('change.select2');
                        }
                        $doctorField.trigger('change');
                    }
                });
            }
        });
    });
})(django.jQuery);