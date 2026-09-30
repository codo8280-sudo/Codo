import 'package:flutter/material.dart';

class CodoSearchField extends StatefulWidget {
  const CodoSearchField({
    super.key,
    required this.onSubmitted,
    this.hint = 'Recherchez une loi, un article, une procedure ou posez votre question',
  });

  final ValueChanged<String> onSubmitted;
  final String hint;

  @override
  State<CodoSearchField> createState() => _CodoSearchFieldState();
}

class _CodoSearchFieldState extends State<CodoSearchField> {
  final controller = TextEditingController();

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      minLines: 1,
      maxLines: 4,
      textInputAction: TextInputAction.search,
      onSubmitted: (value) {
        final query = value.trim();
        if (query.isNotEmpty) widget.onSubmitted(query);
      },
      decoration: InputDecoration(
        hintText: widget.hint,
        prefixIcon: const Icon(Icons.search_rounded),
        suffixIcon: IconButton(
          tooltip: 'Recherche vocale - integration a venir',
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('La recherche vocale sera connectee dans un prochain increment.')),
            );
          },
          icon: const Icon(Icons.mic_none_rounded),
        ),
      ),
    );
  }
}
