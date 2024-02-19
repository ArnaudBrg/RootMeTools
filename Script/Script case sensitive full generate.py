def generate_password_variants(password):
    variants = []

    def generate_helper(current_variant, remaining_chars):
        if not remaining_chars:
            variants.append(current_variant)
            return

        # Casse minuscule
        generate_helper(current_variant + remaining_chars[0].lower(), remaining_chars[1:])
        # Casse majuscule
        generate_helper(current_variant + remaining_chars[0].upper(), remaining_chars[1:])

    generate_helper("", password)
    return variants

# Exemple avec le mot de passe "e2azo93i"
password = "e2azo93i"
all_variants = generate_password_variants(password)

# Afficher les résultats
for variant in all_variants:
    print(variant)
